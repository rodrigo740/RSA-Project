/*!
=========================================================
* Argon Dashboard React - v1.1.0
=========================================================
* Product Page: https://www.creative-tim.com/product/argon-dashboard-react
* Copyright 2019 Creative Tim (https://www.creative-tim.com)
* Licensed under MIT (https://github.com/creativetimofficial/argon-dashboard-react/blob/master/LICENSE.md)
* Coded by Creative Tim
=========================================================
* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/
import React, {useState,useEffect} from "react";
// react plugin used to create google maps
// reactstrap components
import {Card, Container, Row, Col, CardHeader, CardTitle, CardBody} from "reactstrap";
// core components
import Maps from "./Maps_Component.js";

import ReactSpeedometer from "react-d3-speedometer"

const call_time = 200;


const Maps_Page = () => {

  const [markers, setMarkers] = useState([]);
  // const [speeds, setSpeeds] = useState([]);
  //const [leader, setLeader] = useState([]);

  useEffect(() => {
    const interval = setInterval(
      () => {
        getLocations().then((value) => {
          setMarkers(value)
        }
        
        
        );/*
        getLeaders().then((value) => {
          setLeader(value)
        });*/
        // getSpeed().then((value) => {
        //   setSpeeds(value)
        // });
      }, call_time);

      return () => clearInterval(interval)
    },[]
  )

  const getLocations = async () => {
    let response = await fetch(
      `http://localhost:8000/getLocations`);
      //console.log(response)
    let result = await response.json();
    let all_locations = [];
    //console.log("Results: ")
    //console.log(result)
    for (var obu in result) {
      
      all_locations.push(
        {
          lat: Number(result[obu]["lat"]),
          lng: Number(result[obu]["lng"]),
          id: result[obu]["id"],
          speed: Number(result[obu]["spd"]),
          leader: result[obu]["leader"]
        }
      )
    }
    //console.log(all_locations)
    return all_locations;
  }

  const getLeaders = async () => {
    let response = await fetch(
      `http://localhost:8000/getLeaders`);
      //console.log(response)
    let result = await response.json();
    //console.log(result)
    let res = [{"leader": result["last"]}];
    
    //console.log("RES NEXT")
    //console.log(res)
    
    return res;
  }


  return(
      <>
        {/* Page content */}
        <Container className="mt--7" fluid>
          <Row>
            <div className="col">
              <Card className="shadow border-0">
                <Maps
                  markers={markers}
                  zoom = {10}
                  mapElement={
                    <div style={{ height: `100%`, borderRadius: "inherit" }} />
                  }
                />
              </Card>
            </div>
          </Row>
          <Row>
            <Col md="3">
              <Card>
                <CardHeader>
                  <CardTitle tag="h5">Speed Car 1</CardTitle>
                </CardHeader>
                <CardBody style={{ height: "266px" }}>
                  <ReactSpeedometer
                    value={120||markers[0].speed}
                    segments={5}
                    segmentColors={[
                      "#bf616a",
                      "#d08770",
                      "#ebcb8b",
                      "#a3be8c",
                      "#b48ead",
                    ]}
                    // startColor will be ignored
                    // endColor will be ignored
                  />
                </CardBody>
              </Card>
            </Col>
            <Col md="3">
              <Card>
                <CardHeader>
                  <CardTitle tag="h5">Speed Car 2</CardTitle>
                </CardHeader>
                <CardBody style={{ height: "266px" }}>
                <ReactSpeedometer
                    value={120||markers[1].speed}
                    segments={5}
                    segmentColors={[
                      "#bf616a",
                      "#d08770",
                      "#ebcb8b",
                      "#a3be8c",
                      "#b48ead",
                    ]}
                    // startColor will be ignored
                    // endColor will be ignored
                  />
                </CardBody>
              </Card>
            </Col>
            <Col md="3">
              <Card>
                <CardHeader>
                  <CardTitle tag="h5">Speed Car 3</CardTitle>
                </CardHeader>
                <CardBody style={{ height: "266px" }}>
                <ReactSpeedometer
                    value={100||markers[2].speed}
                    segments={5}
                    segmentColors={[
                      "#bf616a",
                      "#d08770",
                      "#ebcb8b",
                      "#a3be8c",
                      "#b48ead",
                    ]}
                    // startColor will be ignored
                    // endColor will be ignored
                  />
                </CardBody>
              </Card>
            </Col>
            <Col md="3">
              <Card>
                <CardHeader>
                  <CardTitle tag="h5">Speed Car 4</CardTitle>
                </CardHeader>
                <CardBody style={{ height: "266px" }}>
                <ReactSpeedometer
                    value={100||markers[3].speed}
                    segments={5}
                    segmentColors={[
                      "#bf616a",
                      "#d08770",
                      "#ebcb8b",
                      "#a3be8c",
                      "#b48ead",
                    ]}
                    // startColor will be ignored
                    // endColor will be ignored
                  />
                </CardBody>
              </Card>
            </Col>
        </Row>
        </Container>
      </>
    );
  }

export default Maps_Page;
