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
import {Card, Container, Row} from "reactstrap";
// core components
import Maps from "./Maps_Component.js";

const call_time = 200;


const Maps_Page = () => {

  const [markers, setMarkers] = useState([]);
  const [leader, setLeader] = useState([]);

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
      }, call_time);

      return () => clearInterval(interval)
    },[]
  )

  const getLocations = async () => {
    let response = await fetch(
      `http://localhost:8000/getLocations`);
      console.log(response)
    let result = await response.json();
    let all_locations = [];
    console.log("Results: ")
    console.log(result)
    for (var obu in result) {
      
      all_locations.push(
        {
          lat: result[obu]["lat"]/10000000,
          lng: result[obu]["lng"]/10000000,
          id: result[obu]["id"],
          leader: result[obu]["leader"]
        }
      )
    }
    console.log(all_locations)
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
        </Container>
      </>
    );
  }

export default Maps_Page;
