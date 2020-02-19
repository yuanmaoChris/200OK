import React from "react";
import { Button, Form, FormGroup, Input, Label } from "reactstrap";
import axios from "axios";

import { API_URL } from "../constants";

class NewPostForm extends React.Component {
    state = {
        id: 0,
        user_id: "",
        content: "",
        pub_date: "",
        visibility: ""
    };

    componentDidMount() {
        if (this.props.post) {
            const { id, user_id, content, pub_date, visibility } = this.props.post;
            this.setState({ id, user_id, content, pub_date, visibility });
        }
    }

    onChange = e => {
        this.setState({ [e.target.name]: e.target.value });
    };

    createPost = e => {
        e.preventDefault();
        axios.post(API_URL, this.state).then(() => {
            this.props.resetState();
            this.props.toggle();
        });
    };

    editPost = e => {
        e.preventDefault();
        axios.put(API_URL + this.state.id, this.state).then(() => {
            this.props.resetState();
            this.props.toggle();
        });
    };

    defaultIfEmpty = value => {
        return value === "" ? "" : value;
    };

    render() {
        return (
            <Form onSubmit={this.props.post ? this.editPost : this.createPost}>
                <FormGroup>
                    <Label for="user_id">user_id:</Label>
                    <Input
                        type="text"
                        name="user_id"
                        onChange={this.onChange}
                        value={this.defaultIfEmpty(this.state.user_id)}
                    />
                </FormGroup>
                <FormGroup>
                    <Label for="content">Content:</Label>
                    <Input
                        type="text"
                        name="content"
                        onChange={this.onChange}
                        value={this.defaultIfEmpty(this.state.content)}
                    />
                </FormGroup>
                <FormGroup>
                    <Label for="pub_date">Published Date:</Label>
                    <Input
                        type="date"
                        name="pub_date"
                        onChange={this.onChange}
                        value={this.defaultIfEmpty(this.state.pub_date)}
                    />
                </FormGroup>
                <FormGroup>
                    <Label for="visibility">Visibility:</Label>
                    <Input
                        type="text"
                        name="visibility"
                        onChange={this.onChange}
                        value={this.defaultIfEmpty(this.state.visibility)}
                    />
                </FormGroup>
                <Button>Submit</Button>
            </Form>
        );
    }
}

export default NewPostForm;