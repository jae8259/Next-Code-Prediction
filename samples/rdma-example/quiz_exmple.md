The original code like this. Even though this is a simple and class client accepting code, there are lots resource management code, so it is very hard to understand the strucuture of the code at an instant.
```c
static int accept_client_connection()
{
	struct rdma_conn_param conn_param;
	struct rdma_cm_event *cm_event = NULL;
	struct sockaddr_in remote_sockaddr; 
	int ret = -1;
	if(!cm_client_id || !client_qp) {
		rdma_error("Client resources are not properly setup\n");
		return -EINVAL;
	}
	/* we prepare the receive buffer in which we will receive the client metadata*/
    client_metadata_mr = rdma_buffer_register(pd /* which protection domain */, 
			&client_metadata_attr /* what memory */,
			sizeof(client_metadata_attr) /* what length */, 
		       (IBV_ACCESS_LOCAL_WRITE) /* access permissions */);
	if(!client_metadata_mr){
		rdma_error("Failed to register client attr buffer\n");
		//we assume ENOMEM
		return -ENOMEM;
	}
	/* We pre-post this receive buffer on the QP. SGE credentials is where we 
	 * receive the metadata from the client */
	client_recv_sge.addr = (uint64_t) client_metadata_mr->addr; // same as &client_buffer_attr
	client_recv_sge.length = client_metadata_mr->length;
	client_recv_sge.lkey = client_metadata_mr->lkey;
	/* Now we link this SGE to the work request (WR) */
	bzero(&client_recv_wr, sizeof(client_recv_wr));
	client_recv_wr.sg_list = &client_recv_sge;
	client_recv_wr.num_sge = 1; // only one SGE
	ret = ibv_post_recv(client_qp /* which QP */,
		      &client_recv_wr /* receive work request*/,
		      &bad_client_recv_wr /* error WRs */);
	if (ret) {
		rdma_error("Failed to pre-post the receive buffer, errno: %d \n", ret);
		return ret;
	}
	debug("Receive buffer pre-posting is successful \n");
	/* Now we accept the connection. Recall we have not accepted the connection 
	 * yet because we have to do lots of resource pre-allocation */
       memset(&conn_param, 0, sizeof(conn_param));
       /* this tell how many outstanding requests can we handle */
       conn_param.initiator_depth = 3; /* For this exercise, we put a small number here */
       /* This tell how many outstanding requests we expect other side to handle */
       conn_param.responder_resources = 3; /* For this exercise, we put a small number */
       ret = rdma_accept(cm_client_id, &conn_param);
       if (ret) {
	       rdma_error("Failed to accept the connection, errno: %d \n", -errno);
	       return -errno;
       }
       /* We expect an RDMA_CM_EVNET_ESTABLISHED to indicate that the RDMA  
	* connection has been established and everything is fine on both, server 
	* as well as the client sides.
	*/
        debug("Going to wait for : RDMA_CM_EVENT_ESTABLISHED event \n");
       ret = process_rdma_cm_event(cm_event_channel, 
		       RDMA_CM_EVENT_ESTABLISHED,
		       &cm_event);
        if (ret) {
		rdma_error("Failed to get the cm event, errnp: %d \n", -errno);
		return -errno;
	}
	/* We acknowledge the event */
	ret = rdma_ack_cm_event(cm_event);
	if (ret) {
		rdma_error("Failed to acknowledge the cm event %d\n", -errno);
		return -errno;
	}
	/* Just FYI: How to extract connection information */
	memcpy(&remote_sockaddr /* where to save */, 
			rdma_get_peer_addr(cm_client_id) /* gives you remote sockaddr */, 
			sizeof(struct sockaddr_in) /* max size */);
	printf("A new connection is accepted from %s \n", 
			inet_ntoa(remote_sockaddr.sin_addr));
	return ret;
}
```

I want the quiz to be in this form
```c
// INSTRUCTION: include 5 lines at least to give me the context. Also, if I think the context isn't enough, you must provide a key to expand previous lines
	/* we prepare the receive buffer in which we will receive the client metadata*/
    client_metadata_mr = ____(pd /* which protection domain */, 
			&client_metadata_attr /* what memory */,
			sizeof(client_metadata_attr) /* what length */, 
		       (IBV_ACCESS_LOCAL_WRITE) /* access permissions */);
// INSTRUCTION: Same for the later contexts.
```
So, i need to guess the what ____ should be. If I'm wrong, it should provide an interface like this.
```sh
The answer was `rdma_buffer_register`.
Press c to continue, m to see manual or r to make a review note...
```
I know some functions aren't documented or it doesn't have a manual page. But for now, I want some features like `m` maps to the result of `man some function`. If it doesn't have one, just print out "No manual provided." and "Press c to continue, m to see manual or r to make a review note..."
The result would look like this
```sh
The answer was `rdma_buffer_register`.
Press c to continue, m to see manual or r to make a review note...
// Pressed m
No manual provided.
Press c to continue, m to see manual or r to make a review note...
```
If I make a review note, save a text file like this for now.
```txt
    client_metadata_mr = ____(pd /* which protection domain */, 
			&client_metadata_attr /* what memory */,
			sizeof(client_metadata_attr) /* what length */, 
		       (IBV_ACCESS_LOCAL_WRITE) /* access permissions */);
a: rdma_buffer_registe
```
I want you to make a separate module for this, as I'm going to make profound review note in the future.
The review note generator (you could use any design pattern you want, possibly a factory) should at least have two interfaces
```python
get_question(question:AbstractQuestion) # This recieves a question
generate_review_note(note:ReviewNoteFactory) # The review note factory parses the Question and then make a writable-note. So, reivew note generator merely saves the review note while implementations are in somewhere else.
```
For now we will only have `FunctionQuestion` and `SimpleNote` class where the former just makes a blank and the latter just saves the question with the answer. The separation is to be aware of expanding the program to use with DBMS, but for now this is a small project so we will just save it under `review` foldre in the project directory

Now, about the UI. I want to use "Textual" to highlight blanks into red. Right now you just pring underbars, so it really confuses me. 

Also, it would be really great if we add syntac highlighting support using LSP servers. But if you think this is too hard, let's leave it beside. Actually you must leave it beside it this can not be done within a hundreds of lines. Rather, you should write report why this is hard and what else could be nice.