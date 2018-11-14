*API for a blog with authentication.*

This app uses local memory as its database, which means all users, posts, and JWT tokens will be lost whenever the server is restarted.

The JWT tokens are good for 45 minutes.

Here is a list of the routes and what they do:

Start here:


'/users' POST
Pass JSON to create an account. Example:
{ "name":"kurt", "password":"kurtspassword"}
This will create a user in memory of the form: id, username, hashed_password.


'/users/login' POST
In Postman (or similar app), use 'Basic Auth' to input the username and password you just used to create an account. A unique JWT token will be passed back to you.


Use the token to explore all parts of the API that require authentication:


'/users' GET
Get a list of all users.


'/users/<id>' GET
View a particular user.


'/users/<id>' PUT
Change your name or password. (May not be working yet. You may even be able to change another user's name and password!)


'/users/<id>' DELETE
Delete your account. (You may be able to delete other users' accounts, too.)


'/myposts' GET
Get a list of all posts that you wrote.


'/allposts' GET
Get a list of all posts written by all users.


'/myposts/<post_id>' GET
View a particular post that you wrote.


'/myposts' POST
Create a post. Format the JSON to be passed in as:
{ "title":"Post Title", "content":"Post content..."}


'/myposts/<id>' PUT
Modify a post. Format JSON as:
{ "title":"Post Title", "content":"Post content..."}


'/myposts/<id>' DELETE
Delete a post.
