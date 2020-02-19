import React, { Component } from 'react';
import Background from '../images/background.jpg';
import ReactDOM from 'react-dom';

var sectionStyle = {
    // width: "100%",
    backgroundImage: "url(" + { Background } + ")"
  };


// const main = <h1>Hello, world</h1>;
// ReactDOM.render(main, document.getElementById('root'));

class Main extends Component{

    render(){
        return (
            // <section style={ sectionStyle } className='App'>
            // </section>
            <div className="bg">
                <p>Hello World.</p>
            </div>
          );
    }
}

export default Main;


