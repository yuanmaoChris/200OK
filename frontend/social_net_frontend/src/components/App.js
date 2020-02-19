import React, { Component } from 'react';
import { HashRouter as Router, Route, Link, NavLink } from 'react-router-dom';
import { Redirect } from 'react-router';
import SignUpForm from '../components/SignUp';
import SignInForm from '../components/SignIn';
import MainPage from '../components/Main';

import '../stylesheets/App.css';

class App extends Component {

  constructor() {
    super();
    this.state = {
        signInStatus:false,
        signUpStatus:false,
    }
    this.handleSignUp = this.handleSignUp.bind(this);
    this.handleSignIn = this.handleSignIn.bind(this);
  }

  handleSignUp = async (status) =>{
      await this.setState({signUpStatus:status});
      console.log(this.state.signUpStatus);
  }

  handleSignIn = async (status) =>{
      await this.setState({signInStatus:status});
  }

  render() {
    if(this.state.signInStatus || this.state.signUpStatus){
      // this.setState({signInStatus:false, signUpStatus:false});
      return(
          <Router basename="/main">
            <MainPage></MainPage>
          </Router>
      );
    }
    
    return(
      <Router>
      <div className="App">
        <div className="App__Aside"></div>
          <div className="App__Form">
              <div className="PageSwitcher">
                  <NavLink exact to="/" activeClassName="PageSwitcher__Item--Active" className="PageSwitcher__Item">Sign In</NavLink>
                  <NavLink to="/sign-up" activeClassName="PageSwitcher__Item--Active" className="PageSwitcher__Item">Sign Up</NavLink>
              </div>
    
              <div className="FormTitle">
                  <NavLink exact to="/" activeClassName="FormTitle__Link--Active" className="FormTitle__Link">Sign In</NavLink>
                   or 
                  <NavLink to="/sign-up" activeClassName="FormTitle__Link--Active" className="FormTitle__Link">Sign Up</NavLink>
              </div>
     
              {/* <Route exact path="/" component={SignUpForm}>
              </Route> */}
              <Route path="/sign-up">
                <SignUpForm callbackSignUp={this.handleSignUp}></SignUpForm>
              </Route>
              <Route exact path="/">
                <SignInForm callbackSignIn={this.handleSignIn}></SignInForm>
              </Route>
              <Route path="/main">
                <MainPage/>
              </Route>
          </div>
      </div>
    
      </Router>);

  }
}

export default App;
