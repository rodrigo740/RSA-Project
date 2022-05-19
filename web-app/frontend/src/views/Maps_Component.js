import React from "react";
// react plugin used to create google maps
import { GoogleMap, Marker, withGoogleMap, withScriptjs } from "react-google-maps";
// core components
var iconBase = 'http://maps.google.com/mapfiles/kml/pal4/';


const MapWithAMarker = withScriptjs(
  withGoogleMap(props =>
    <GoogleMap
      defaultZoom={12}
      defaultCenter={{ lat: 40.64337, lng: -8.65915 }}
    >

      {props.markers.map((props, index) => {
        //console.log(props.leader)
        if (props.leader == "0") {
          return (
            <Marker position={{ lat: props.lat, lng: props.lng }}
              key={index}
              id={index}
              icon={iconBase + 'icon15.png'}
              onClick={(() => {
              }
              )}
              
            />
          )
        } else {
          return (
            <Marker position={{ lat: props.lat, lng: props.lng }}
              key={index}
              id={index}
              icon={iconBase + 'icon62.png'}
              onClick={(() => {
              }
              )}
              
            />
          )
        }
        
      })}
    </GoogleMap>
  ));

class Maps extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      lat: 0,
      lng: 0
    }
  }
  /*
  componentDidMount(){
    Promise.all([this.get_my_location()]).then((value) => {
      this.setState(
        {
          lat: value[0].coords.latitude,
          lng: value[0].coords.longitude
        })})
  }*/

  get_my_location = () => {
    if (navigator.geolocation) {
      return new Promise(
        (resolve, reject) => navigator.geolocation.getCurrentPosition(resolve, reject)
      )
    } else {
      return new Promise(
        resolve => resolve({})
      )
    }
  }

  render() {
    return (<MapWithAMarker
      googleMapURL="https://maps.googleapis.com/maps/api/js?key=AIzaSyCPp6sTC61YbWoKMaLVWZ2f4kR5MG1WdKg&v=3.exp&libraries=geometry,drawing,places"
      loadingElement={<div style={{ height: `100%` }} />}
      containerElement={<div style={{ height: `400px` }} />}
      mapElement={<div style={{ height: `100%` }} />}
      markers={this.props.markers}
      options={{
        gestureHandling: 'greedy',
        zoomControlOptions: { position: 9 },
        streetViewControl: false,
        fullscreenControl: true,
      }}
    />);
  }
}

export default Maps;
