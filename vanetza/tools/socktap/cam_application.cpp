#include "cam_application.hpp"
#include "complete_packet.hpp"
#include <vanetza/btp/ports.hpp>
#include <vanetza/asn1/cam.hpp>
#include <vanetza/asn1/packet_visitor.hpp>
#include <vanetza/facilities/cam_functions.hpp>
#include <boost/units/cmath.hpp>
#include <boost/units/systems/si/prefixes.hpp>
#include <boost/asio.hpp>
#include <chrono>
#include <exception>
#include <functional>
#include <iostream>

using namespace vanetza;
using namespace vanetza::facilities;
using namespace std::chrono;
using json = nlohmann::json;
using namespace boost::asio;

std::map<long, std::map<std::string, double>> persistence;

prometheus::Counter *cam_rx_counter;
prometheus::Counter *cam_tx_counter;
prometheus::Counter *cam_rx_latency;
prometheus::Counter *cam_tx_latency;

boost::asio::io_service cam_io_service_;
ip::udp::socket cam_udp_socket(cam_io_service_);
ip::udp::endpoint cam_remote_endpoint;
boost::system::error_code cam_err;

SpeedValue_t last_speed = LLONG_MIN;
double time_speed = 0;

HeadingValue_t last_heading = LLONG_MIN;
double time_heading = 0;

CamApplication::CamApplication(PositionProvider& positioning, Runtime& rt, Mqtt *mqtt_, Dds* dds_, config_t config_s_, metrics_t metrics_s_) :
    positioning_(positioning), runtime_(rt), cam_interval_(seconds(1)), mqtt(mqtt_), dds(dds_), config_s(config_s_), metrics_s(metrics_s_)
{
    persistence = {};
    if(config_s.cam.mqtt_enabled) mqtt->subscribe(config_s.cam.topic_in, this);
    if(config_s.cam.mqtt_enabled) mqtt->subscribe(config_s.full_cam_topic_in, this);
    if(config_s.cam.dds_enabled) dds->subscribe(config_s.cam.topic_in, this);
    if(config_s.cam.dds_enabled) dds->subscribe(config_s.full_cam_topic_in, this);
    
    cam_rx_counter = &((*metrics_s.packet_counter).Add({{"message", "cam"}, {"direction", "rx"}}));
    cam_tx_counter = &((*metrics_s.packet_counter).Add({{"message", "cam"}, {"direction", "tx"}}));
    cam_rx_latency = &((*metrics_s.latency_counter).Add({{"message", "cam"}, {"direction", "rx"}}));
    cam_tx_latency = &((*metrics_s.latency_counter).Add({{"message", "cam"}, {"direction", "tx"}}));

    if(config_s.cam.udp_out_port != 0) {
        cam_udp_socket.open(ip::udp::v4());
        cam_remote_endpoint = ip::udp::endpoint(ip::address::from_string(config_s.cam.udp_out_addr), config_s.cam.udp_out_port);
    }
}

void CamApplication::set_interval(Clock::duration interval)
{
    cam_interval_ = interval;
    runtime_.cancel(this);
    if (interval != std::chrono::milliseconds(0)) schedule_timer();
}

CamApplication::PortType CamApplication::port()
{
    return btp::ports::CAM;
}

void CamApplication::indicate(const DataIndication& indication, UpPacketPtr packet)
{
    struct indication_visitor : public boost::static_visitor<CohesivePacket>
    {
        CohesivePacket operator()(CohesivePacket& packet) {return packet;}
        CohesivePacket operator()(ChunkPacket& packet) {return CohesivePacket(std::move(ByteBuffer()), OsiLayer::Physical);}
    } ivis;

    UpPacket* packet_ptr = packet.get();
    CohesivePacket cp = boost::apply_visitor(ivis, *packet_ptr);

    asn1::PacketVisitor<asn1::Cam> visitor;
    std::shared_ptr<const asn1::Cam> cam = boost::apply_visitor(visitor, *packet);

    std::cout << "CAM application received a packet with " << (cam ? "decodable" : "broken") << " content" << std::endl;

    CAM_t cam_t = {(*cam)->header, (*cam)->cam};
    string cam_json = buildJSON(cam_t, cp.time_received, cp.rssi);

    if(config_s.cam.mqtt_enabled) mqtt->publish(config_s.cam.topic_out, cam_json);
    if(config_s.cam.dds_enabled) dds->publish(config_s.cam.topic_out, cam_json);
    std::cout << "CAM JSON: " << cam_json << std::endl;
    cam_rx_counter->Increment();

    if(config_s.full_cam_topic_out != "") { 
        json fields_json = cam_t;
        json full_json = {
            {"timestamp", cp.time_received},
            {"rssi", cp.rssi},
            {"others", {
                "json_timestamp", (double) duration_cast< milliseconds >(system_clock::now().time_since_epoch()).count() / 1000.0}
            },
            {"fields", fields_json}
        };
        string json_dump = full_json.dump();
        if(config_s.cam.mqtt_enabled) mqtt->publish(config_s.full_cam_topic_out, json_dump);
        if(config_s.cam.dds_enabled) dds->publish(config_s.full_cam_topic_out, json_dump);
        if(config_s.cam.udp_out_port != 0) {
            cam_udp_socket.send_to(buffer(json_dump, json_dump.length()), cam_remote_endpoint, 0, cam_err);
        }
    }
}

void CamApplication::schedule_timer()
{
    runtime_.schedule(cam_interval_, std::bind(&CamApplication::on_timer, this, std::placeholders::_1), this);
}

std::string CamApplication::buildJSON(CAM_t message, double time_reception, int rssi) { 
    ItsPduHeader_t& header = message.header;
    CoopAwareness_t& cam = message.cam;
    BasicContainer_t& basic = cam.camParameters.basicContainer;
    BasicVehicleContainerHighFrequency& bvc = cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency;
    AccelerationControl_t* acc = cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.accelerationControl;
    //json j = cam;
    //std::cout << "CAM JSON: " << j << std::endl;

    string driveDirection = "UNAVAILABLE"; 
    switch(bvc.driveDirection) {
        case(0):
            driveDirection = "FORWARD";
            break;
        case(1):
            driveDirection = "BACKWARD";
            break;
        default:
            driveDirection = "UNAVAILABLE";
            break;
    }

    long latitude = (long) basic.referencePosition.latitude;
    long longitude = (long) basic.referencePosition.longitude;

    auto last_map = persistence.find(header.stationID);
    
    bool new_info = last_map == persistence.end() || ((last_map->second)["lat"] != (double) latitude) || ((last_map->second)["lng"] != (double) longitude) || ( time_reception - (last_map->second)["time"] >= 1);

    const double time_now = (double) duration_cast< milliseconds >(system_clock::now().time_since_epoch()).count() / 1000.0;

    json json_payload = {
            {"timestamp", time_reception},
            {"newInfo", new_info},
            {"rssi", rssi},
            {"test", {
                {"json_timestamp", time_now}
            }
            },
            {"stationID", (long) header.stationID},
            {"stationType", (long) basic.stationType},
            {"receiverID", config_s.station_id},
            {"receiverType", config_s.station_type},
            {"latitude", latitude},
            {"longitude", longitude},
            {"semiMajorConf", (long) basic.referencePosition.positionConfidenceEllipse.semiMajorConfidence},
            {"semiMinorConf", (long) basic.referencePosition.positionConfidenceEllipse.semiMinorConfidence},
            {"semiMajorOrient", (long) basic.referencePosition.positionConfidenceEllipse.semiMajorOrientation},
            {"altitude", (long) basic.referencePosition.altitude.altitudeValue},
            {"altitudeConf", (long) basic.referencePosition.altitude.altitudeConfidence},
            {"heading", (long) bvc.heading.headingValue},
            {"headingConf", (long) bvc.heading.headingConfidence},
            {"speed", (long) bvc.speed.speedValue},
            {"speedConf", (long) bvc.speed.speedConfidence},
            {"driveDirection", driveDirection},
            {"length",(long) bvc.vehicleLength.vehicleLengthValue},
            {"width", (long) bvc.vehicleWidth},
            {"acceleration", (long) bvc.longitudinalAcceleration.longitudinalAccelerationValue},
            {"curvature", (long) bvc.curvature.curvatureValue},
            {"yawRate", (long) bvc.yawRate.yawRateValue},
            {"brakePedal", (bool) (*(bvc.accelerationControl->buf) & (1 << (7-0)))},
            {"gasPedal", (bool) (*(bvc.accelerationControl->buf) & (1 << (7-1)))},
            {"emergencyBrake", (bool) (*(bvc.accelerationControl->buf) & (1 << (7-2)))},
            {"collisionWarning", (bool) (*(bvc.accelerationControl->buf) & (1 << (7-3)))},
            {"accEngaged", (bool) (*(bvc.accelerationControl->buf) & (1 << (7-4)))},
            {"cruiseControl", (bool) (*(bvc.accelerationControl->buf) & (1 << (7-5)))},
            {"speedLimiter", (bool) (*(bvc.accelerationControl->buf) & (1 << (7-6)))},
            {"specialVehicle", {
                  {"publicTransportContainer", {
                     {"embarkationStatus", false}
                  }
                  }
            }}
    };

    if(new_info) persistence[header.stationID] = {{"lat", (double) latitude}, {"lng", (double) longitude}, {"time", time_reception}};

    cam_rx_latency->Increment(time_now - time_reception);
    return json_payload.dump();
}

void CamApplication::on_message(string topic, string mqtt_message) {

    const double time_reception = (double) duration_cast< milliseconds >(system_clock::now().time_since_epoch()).count() / 1000.0;

    json payload;

    try {
        payload = json::parse(mqtt_message);
    } catch(nlohmann::detail::type_error& e) {
        std::cout << "-- Vanetza JSON Decoding Error --\nCheck that the message format follows JSON spec\n" << e.what() << std::endl;
        return;
    } catch(...) {
        std::cout << "-- Unexpected Error --\nVanetza couldn't decode the JSON message.\nNo other info available\n" << std::endl;
        return;
    }

    vanetza::asn1::Cam message;
    CoopAwareness_t cam;
    ItsPduHeader_t& header = message->header;
    header.protocolVersion = 2;  
    header.messageID = ItsPduHeader__messageID_cam;

    if(topic == config_s.full_cam_topic_in) {
        try {
            cam = payload.get<CoopAwareness_t>();
        } catch(nlohmann::detail::type_error& e) {
            std::cout << "-- Vanetza ETSI Decoding Error --\nCheck that the message format follows ETSI spec\n" << e.what() << std::endl;
            return;
        } catch(...) {
            std::cout << "-- Unexpected Error --\nVanetza couldn't decode the JSON message.\nNo other info available\n" << std::endl;
            return;
        }

        header.stationID = config_s.station_id;
        message->cam = cam;
    }
    else if(topic == config_s.cam.topic_in) {
        try {
            cam = message->cam;
            header.stationID = payload["stationID"];
            const auto time_now = duration_cast<milliseconds>(runtime_.now().time_since_epoch());
            uint16_t gen_delta_time = time_now.count();
            cam.generationDeltaTime = gen_delta_time * GenerationDeltaTime_oneMilliSec;
            cam.camParameters.basicContainer.referencePosition.latitude = payload["latitude"];
            cam.camParameters.basicContainer.referencePosition.longitude = payload["longitude"];
            cam.camParameters.basicContainer.referencePosition.positionConfidenceEllipse.semiMajorConfidence = payload["semiMajorConf"];
            cam.camParameters.basicContainer.referencePosition.positionConfidenceEllipse.semiMinorConfidence = payload["semiMinorConf"];
            cam.camParameters.basicContainer.referencePosition.positionConfidenceEllipse.semiMajorOrientation = payload["semiMajorOrient"];
            cam.camParameters.basicContainer.referencePosition.altitude.altitudeValue = payload["altitude"];
            cam.camParameters.basicContainer.referencePosition.altitude.altitudeConfidence = payload["altitudeConf"];
            cam.camParameters.basicContainer.stationType = payload["stationType"];
            cam.camParameters.highFrequencyContainer.present = HighFrequencyContainer_PR_basicVehicleContainerHighFrequency;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.heading.headingValue = payload["heading"];
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.heading.headingConfidence = payload["headingConf"];
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.speed.speedValue = payload["speed"];
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.speed.speedConfidence = payload["speedConf"];
            if(payload["driveDirection"] == "FORWARD") cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.driveDirection = DriveDirection_forward;
            else if(payload["driveDirection"] == "BACKWARD") cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.driveDirection = DriveDirection_backward;
            else cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.driveDirection = DriveDirection_unavailable;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.vehicleLength.vehicleLengthValue = payload["length"];
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.vehicleWidth = payload["width"];
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.longitudinalAcceleration.longitudinalAccelerationValue = payload["acceleration"];
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.curvature.curvatureValue = payload["curvature"];
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.yawRate.yawRateValue = payload["yawRate"];
            AccelerationControl_t* p_tmp = vanetza::asn1::allocate<AccelerationControl_t>();
            bool brakePedalEngaged;
            bool gasPedalEngaged;
            bool emergencyBrakeEngaged;
            bool collisionWarningEngaged;
            bool accEngaged;
            bool cruiseControlEngaged;
            bool speedLimiterEngaged;
            payload.at("brakePedal").get_to((brakePedalEngaged));
            payload.at("gasPedal").get_to((gasPedalEngaged));
            payload.at("emergencyBrake").get_to((emergencyBrakeEngaged));
            payload.at("collisionWarning").get_to((collisionWarningEngaged));
            payload.at("accEngaged").get_to((accEngaged));
            payload.at("cruiseControl").get_to((cruiseControlEngaged));
            payload.at("speedLimiter").get_to((speedLimiterEngaged));
            p_tmp->size = (7 / 8) + 1;
            p_tmp->bits_unused = 8 - (7 % 8);
            p_tmp->buf = (uint8_t *) calloc(1, sizeof(uint8_t) * p_tmp->size);
            *(p_tmp->buf + (sizeof(uint8_t) * 0)) = (uint8_t) 0;
            if (brakePedalEngaged) *(p_tmp->buf + (sizeof(uint8_t) * 0)) |= (1 << 7);
            if (gasPedalEngaged) *(p_tmp->buf + (sizeof(uint8_t) * 0)) |= (1 << 6);
            if (emergencyBrakeEngaged) *(p_tmp->buf + (sizeof(uint8_t) * 0)) |= (1 << 5);
            if (collisionWarningEngaged) *(p_tmp->buf + (sizeof(uint8_t) * 0)) |= (1 << 4);
            if (accEngaged) *(p_tmp->buf + (sizeof(uint8_t) * 0)) |= (1 << 3);
            if (cruiseControlEngaged) *(p_tmp->buf + (sizeof(uint8_t) * 0)) |= (1 << 2);
            if (speedLimiterEngaged) *(p_tmp->buf + (sizeof(uint8_t) * 0)) |= (1 << 1);
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.accelerationControl = p_tmp;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.lanePosition = nullptr;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.steeringWheelAngle = nullptr;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.lateralAcceleration = nullptr;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.verticalAcceleration = nullptr;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.performanceClass = nullptr;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.cenDsrcTollingZone = nullptr;
            cam.camParameters.lowFrequencyContainer = nullptr;
            cam.camParameters.specialVehicleContainer = nullptr;
            SpecialVehicleContainer_t svc = payload.at("specialVehicle").get<SpecialVehicleContainer_t>();
            cam.camParameters.specialVehicleContainer = &svc;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.longitudinalAcceleration.longitudinalAccelerationConfidence = AccelerationConfidence_unavailable;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.yawRate.yawRateConfidence = YawRateConfidence_unavailable;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.heading.headingConfidence = HeadingConfidence_unavailable;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.speed.speedConfidence = SpeedConfidence_unavailable;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.curvature.curvatureConfidence = CurvatureConfidence_unavailable;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.curvatureCalculationMode = CurvatureCalculationMode_yawRateUsed;
            cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency.vehicleLength.vehicleLengthConfidenceIndication = VehicleLengthConfidenceIndication_noTrailerPresent;

            // TEMPORARY
            json j = cam;
            CoopAwareness_t cam2 = j.get<CoopAwareness_t>();
            message->cam = cam2;
        } catch(...) {
            std::cout << "-- Vanetza JSON Decoding Error --\nVanetza couldn't decode the JSON message.\nNo other info available\n" << std::endl;
            return;
        }
    }

    

    DownPacketPtr packet { new DownPacket() };
    packet->layer(OsiLayer::Application) = std::move(message);

    DataRequest request;
    request.its_aid = aid::CA;
    request.transport_type = geonet::TransportType::SHB;
    request.communication_profile = geonet::CommunicationProfile::ITS_G5;

    try {
        auto confirm = Application::request(request, std::move(packet));
        if (!confirm.accepted()) {
            throw std::runtime_error("CAM application data request failed");
        }
    } catch(std::runtime_error& e) {
        std::cout << "-- Vanetza UPER Encoding Error --\nCheck that the message format follows ETSI spec\n" << e.what() << std::endl;
    } catch(...) {
        std::cout << "-- Unexpected Error --\nVanetza couldn't send the requested message but did not throw a runtime error on UPER encode.\nNo other info available\n" << std::endl;
    }

    const double time_now = (double) duration_cast< milliseconds >(system_clock::now().time_since_epoch()).count() / 1000.0;

    cam_tx_counter->Increment();
    cam_tx_latency->Increment(time_now - time_reception);
}

void CamApplication::on_timer(Clock::time_point)
{
    schedule_timer();
    vanetza::asn1::Cam message;

    ItsPduHeader_t& header = message->header;
    header.protocolVersion = 2;
    header.messageID = ItsPduHeader__messageID_cam;
    header.stationID = config_s.station_id;

    const auto time_now = duration_cast<milliseconds>(runtime_.now().time_since_epoch());
    uint16_t gen_delta_time = time_now.count();

    CoopAwareness_t& cam = message->cam;
    cam.generationDeltaTime = gen_delta_time * GenerationDeltaTime_oneMilliSec;

    auto position = positioning_.position_fix();

    SpeedValue_t speed = SpeedValue_unavailable;
    if (position.speed.value().value() >= 0 && position.speed.value().value() <= 16382) speed = position.speed.value().value();
    LongitudinalAccelerationValue_t acceleration = LongitudinalAccelerationValue_unavailable;

    const double millis_now = (double) duration_cast< milliseconds >(system_clock::now().time_since_epoch()).count() / 1000.0;

    if(time_speed == 0) time_speed = millis_now;
    if (last_speed != LLONG_MIN && (speed != last_speed || millis_now - time_speed >= 1)) {
        acceleration = (int)((speed - last_speed) * 10);
        if (acceleration < -160 && acceleration > 160) acceleration = LongitudinalAccelerationValue_unavailable;
        time_speed = millis_now;
    }
    last_speed = speed;

    HeadingValue_t heading = HeadingValue_unavailable;
    if (position.course.value().value() >= 0 && position.course.value().value() <= 3600) heading = position.course.value().value();
    YawRateValue_t yaw_rate = YawRateValue_unavailable;

    if(time_heading == 0) time_heading = millis_now;
    if (last_heading != LLONG_MIN && (heading != last_heading || millis_now - time_heading >= 1)) {
        yaw_rate = (int)((heading - last_heading) * 100);
        if (yaw_rate < -32766 && yaw_rate > 32766) yaw_rate = YawRateValue_unavailable;
        time_heading = millis_now;
    }
    last_heading = heading;

    //if (!position.confidence) {
    //    std::cerr << "Skipping CAM, because no good position is available, yet." << std::endl;
    //    return;
    //}

    BasicContainer_t& basic = cam.camParameters.basicContainer;
    basic.stationType = config_s.station_type;
    copy(position, basic.referencePosition);

    cam.camParameters.highFrequencyContainer.present = HighFrequencyContainer_PR_basicVehicleContainerHighFrequency;

    BasicVehicleContainerHighFrequency& bvc = cam.camParameters.highFrequencyContainer.choice.basicVehicleContainerHighFrequency;
    bvc.heading.headingValue = heading;
    bvc.heading.headingConfidence = HeadingConfidence_unavailable; //position.course.confidence().value();

    bvc.speed.speedValue = speed;
    bvc.speed.speedConfidence = SpeedConfidence_unavailable; //position.speed.confidence().value();

    bvc.driveDirection = DriveDirection_forward;
    bvc.longitudinalAcceleration.longitudinalAccelerationValue = acceleration;

    bvc.vehicleLength.vehicleLengthValue = config_s.length * 10;
    bvc.vehicleLength.vehicleLengthConfidenceIndication = VehicleLengthConfidenceIndication_noTrailerPresent;
    bvc.vehicleWidth = config_s.width * 10;

    bvc.curvature.curvatureValue = CurvatureValue_unavailable;
    bvc.curvature.curvatureConfidence = CurvatureConfidence_unavailable;
    bvc.curvatureCalculationMode = CurvatureCalculationMode_yawRateUsed;

    bvc.yawRate.yawRateValue = yaw_rate;

    bvc.accelerationControl = new AccelerationControl_t();
    bvc.accelerationControl->buf = (uint8_t *) calloc(1, sizeof(uint8_t));
    bvc.accelerationControl->size = 1;
    bvc.accelerationControl->bits_unused = 1;
    *(bvc.accelerationControl->buf) = (uint8_t) 0b10111110;

    std::string error;
    if (!message.validate(error)) {
        throw std::runtime_error("Invalid high frequency CAM: %s" + error);
    }

    DownPacketPtr packet { new DownPacket() };
    packet->layer(OsiLayer::Application) = std::move(message);

    DataRequest request;
    request.its_aid = aid::CA;
    request.transport_type = geonet::TransportType::SHB;
    request.communication_profile = geonet::CommunicationProfile::ITS_G5;

    try {
        auto confirm = Application::request(request, std::move(packet));
        if (!confirm.accepted()) {
            throw std::runtime_error("CAM application data request failed");
        }
    } catch(std::runtime_error& e) {
        std::cout << "-- Vanetza UPER Encoding Error --\nCheck that the message format follows ETSI spec\n" << e.what() << std::endl;
    } catch(...) {
        std::cout << "-- Unexpected Error --\nVanetza couldn't send the requested message but did not throw a runtime error on UPER encode.\nNo other info available\n" << std::endl;
    }

    cam_tx_counter->Increment();
}
