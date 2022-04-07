import React from 'react';
import './Header.css';
import {NavLink} from "react-router-dom";

const Header = () => {

    return (<div className="Header">
            <div className="row">
                <div className="col-sm-12 p-5 mb-4 bg-light rounded-3 jumbotron">
                    <h1 className="text-center title">Self-Learning Systems for Cyber Security</h1>
                    <nav className="navbar navbar-expand-lg navbar-light bg-light">
                    </nav>
                    <ul className="nav nav-tabs justify-content-center navtabsheader">
                        <li className="nav-item navtabheader">
                            <NavLink className="nav-link navtablabel largeFont" to={"emulations"}>
                                Emulations
                            </NavLink>
                        </li>
                        <li className="nav-item navtabheader">
                            <NavLink className="nav-link navtablabel largeFont" to={"simulations"}>
                                Simulations
                            </NavLink>
                        </li>
                        <li className="nav-item navtabheader">
                            <NavLink className="nav-link navtablabel largeFont" to={"monitoring"}>
                                Monitoring
                            </NavLink>
                        </li>
                        <li className="nav-item navtabheader">
                            <NavLink className="nav-link navtablabel largeFont" to={"traces"}>
                                Traces
                            </NavLink>
                        </li>
                        <li className="nav-item navtabheader">
                            <NavLink className="nav-link navtablabel largeFont" to={"dynamicsmodels"}>
                                Dynamics Models
                            </NavLink>
                        </li>
                        <li className="nav-item navtabheader">
                            <NavLink className="nav-link navtablabel largeFont" to={"policyexamination"}>
                                Policy Examination
                            </NavLink>
                        </li>
                        <li className="nav-item navtabheader">
                            <NavLink className="nav-link navtablabel largeFont" to={"images"}>
                                Container Images
                            </NavLink>
                        </li>
                        <li className="nav-item navtabheader">
                            <NavLink className="nav-link navtablabel largeFont" to={"training"}>
                                Training Results
                            </NavLink>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    )
};

Header.propTypes = {};

Header.defaultProps = {};

export default Header;
