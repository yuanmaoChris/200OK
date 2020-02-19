import React, { Component } from "react";
import { Table } from "reactstrap";
import NewPostModal from "./NewPostModal";

import ConfirmRemovalModal from "./ConfirmRemovalModal";

class PostList extends Component {
    render() {
        const posts = this.props.posts;
        return (
            <Table dark>
                <thead>
                    <tr>
                        <th>User_id</th>
                        <th>Content</th>
                        <th>Published Date</th>
                        <th>Visibility</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {!posts || posts.length <= 0 ? (
                        <tr>
                            <td colSpan="6" align="center">
                                <b>Ops, no one here yet</b>
                            </td>
                        </tr>
                    ) : (
                            posts.map(post => (
                                <tr key={post.id}>
                                    <td>{post.user_id}</td>
                                    <td>{post.content}</td>
                                    <td>{post.pub_date}</td>
                                    <td>{post.visibility}</td>
                                    <td align="center">
                                        <NewPostModal
                                            create={false}
                                            post={post}
                                            resetState={this.props.resetState}
                                        />
                                        &nbsp;&nbsp;
                  <ConfirmRemovalModal
                                            id={post.id}
                                            resetState={this.props.resetState}
                                        />
                                    </td>
                                </tr>
                            ))
                        )}
                </tbody>
            </Table>
        );
    }
}

export default PostList;