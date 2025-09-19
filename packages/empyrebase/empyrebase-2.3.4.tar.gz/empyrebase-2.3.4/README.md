# Empyrebase

A simple python wrapper for the [Firebase API](https://firebase.google.com). Supports Realtime DB, Firestore, Auth and Storage.
<p align="center">
<img src="images/empyrebase-logo.png" alt="Empyrebase logo" width="200"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/empyrebase/">
    <img src="https://img.shields.io/pypi/v/empyrebase.svg" alt="PyPI version">
  </a>
  <a href="https://pepy.tech/project/empyrebase">
    <img src="https://pepy.tech/badge/empyrebase" alt="Downloads">
  </a>
  <a href="https://pypi.org/project/empyrebase/">
    <img src="https://img.shields.io/pypi/pyversions/empyrebase.svg" alt="Python Versions">
  </a>
  <a href="https://github.com/emrothenberg/empyrebase/blob/master/LICENSE">
    <img src="https://img.shields.io/pypi/l/empyrebase.svg" alt="License">
  </a>
</p>

## Installation

```shell
pip install empyrebase
```

## Getting Started

### Python Version

Empyrebase was written for python 3 and will not work correctly with python 2.

### Add empyrebase to your application

For use with only user based authentication we can create the following configuration:

```python
import empyrebase

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://databaseName.firebaseio.com",
  "storageBucket": "projectId.appspot.com"
}

firebase = empyrebase.initialize_app(config)
```

This will automatically check for the latest version on PyPI so that you don't miss out on new features. To skip version check:

```
firebase = empyrebase.initialize_app(config, skip_version_check=True)
```

We can optionally add a [service account credential](https://firebase.google.com/docs/server/setup#prerequisites) to our
configuration that will allow our server to authenticate with Firebase as an admin and disregard any security rules.

```python
import empyrebase

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://databaseName.firebaseio.com",
  "storageBucket": "projectId.appspot.com",
  "serviceAccount": "path/to/serviceAccountCredentials.json"
}

firebase = empyrebase.initialize_app(config)
```

Adding a service account will authenticate as an admin by default for all database queries, check out the
[Authentication documentation](#authentication) for how to authenticate users.

### Use Services

An empyrebase app can use multiple Firebase services.

`firebase.auth()` - [Authentication](#authentication)

`firebase.database()` - [Database](#database)

`firebase.storage()` - [Storage](#storage)

`firebase.firestore()` - [Firestore](#firestore)

Check out the documentation for each service for further details.

## Authentication

The `sign_in_with_email_and_password()` method will return user data including a token you can use to adhere to security rules.

Each of the following methods accepts a user token: `get()`, `push()`, `set()`, `update()`, `remove()` and `stream()`.

```python
# Get a reference to the auth service
auth = firebase.auth()

# Log the user in
user = auth.sign_in_with_email_and_password(email, password)

# Log the user in usin OAuth credentials
user = auth.sign_in_with_oauth("oauth_token") # Optional: provider_id. Default: "google.com"

# Log the user in anonymously
user = auth.sign_in_anonymous()

# Add user info
user = auth.update_profile(display_name, photo_url, delete_attribute)

# Get user info
user = auth.get_account_info()

# Get a reference to the database service
db = firebase.database()

# data to save
data = {
    "name": "Mortimer 'Morty' Smith"
}

# Pass the user's idToken to the push method
results = db.child("users").push(data, user['idToken'])
```

In order to obtain the OAuth token for google.com, you'll first need to obtain your client id and secret from GCP console:
1. Go to the url (make sure to enter your actual project id): https://console.cloud.google.com/apis/credentials?pli=1&project=<project_id>
2. Under "OAuth 2.0 Client IDs" find your client and click on the edit button
3. In the "Additional information" column you'll find the client ID, and further down that same column you'll find your client secret.

After obtaining your client ID and secret, you may use the following method to get the OAuth token:
```python
token = auth.get_google_oauth_token("client_id", "client_secret") # Optional: redirect_uri. Default: "http://localhost"
```
Make sure that the redirect_uri (even if just http://localhost) is registered under the "Authorized redirect URIs" section in the client configuration.

### Token expiry

A user's idToken expires after 1 hour, so be sure to use the user's refreshToken to avoid stale tokens.

```
user = auth.sign_in_with_email_and_password(email, password)
# before the 1 hour expiry:
user = auth.refresh(user['refreshToken'])
# now we have a fresh token
user['idToken']
```

### Custom tokens

You can also create users using [custom tokens](https://firebase.google.com/docs/auth/server/create-custom-tokens), for example:

```
token = auth.create_custom_token("your_custom_id")
```

You can also pass in additional claims.

```
token_with_additional_claims = auth.create_custom_token("your_custom_id", {"premium_account": True})
```

You can then send these tokens to the client to sign in, or sign in as the user on the server.

```
user = auth.sign_in_with_custom_token(token)
```

### Manage Users

#### Creating users

```python
auth.create_user_with_email_and_password(email, password)
```

Note: Make sure you have the Email/password provider enabled in your Firebase dashboard under Auth -> Sign In Method.

#### Verifying emails

```python
auth.send_email_verification(user['idToken'])
```

#### Sending password reset emails

```python
auth.send_password_reset_email("email")
```

#### Get account information

```python
auth.get_account_info(user['idToken'])
```

#### Refreshing tokens

```python
user = auth.refresh(user['refreshToken'])
```

#### Delete account

```python
auth.delete_user_account(user['idToken'])
```

## Database

You can build paths to your data by using the `child()` method.

```python
db = firebase.database()
db.child("users").child("Morty")
```

### Save Data

#### push

To save data with a unique, auto-generated, timestamp-based key, use the `push()` method.

```python
data = {"name": "Mortimer 'Morty' Smith"}
db.child("users").push(data)
```

#### set

To create your own keys use the `set()` method. The key in the example below is "Morty".

```python
data = {"name": "Mortimer 'Morty' Smith"}
db.child("users").child("Morty").set(data)
```

#### update

To update data for an existing entry use the `update()` method.

```python
db.child("users").child("Morty").update({"name": "Mortiest Morty"})
```

#### remove

To delete data for an existing entry use the `remove()` method.

```python
db.child("users").child("Morty").remove()
```

#### multi-location updates

You can also perform [multi-location updates](https://www.firebase.com/blog/2015-09-24-atomic-writes-and-more.html) with the `update()` method.

```python
data = {
    "users/Morty/": {
        "name": "Mortimer 'Morty' Smith"
    },
    "users/Rick/": {
        "name": "Rick Sanchez"
    }
}

db.update(data)
```

To perform multi-location writes to new locations we can use the `generate_key()` method.

```python
data = {
    "users/"+ref.generate_key(): {
        "name": "Mortimer 'Morty' Smith"
    },
    "users/"+ref.generate_key(): {
        "name": "Rick Sanchez"
    }
}

db.update(data)
```

#### Conditional Requests

It's possible to do conditional sets and removes by using the `conditional_set()` and `conitional_remove()` methods respectively. You can read more about conditional requests in Firebase [here](https://firebase.google.com/docs/reference/rest/database/#section-conditional-requests).

To use these methods, you first get the ETag of a particular path by using the `get_etag()` method. You can then use that tag in your conditional request.

```python
etag = db.child("users").child("Morty").get_etag()
data = {"name": "Mortimer 'Morty' Smith"}
db.child("users").child("Morty").conditional_set(data, etag["ETag"])
```

If the passed ETag does not match the ETag of the path in the database, the data will not be written, and both conditional request methods will return a single key-value pair with the new ETag to use of the following form:

```json
{ "ETag": "8KnE63B6HiKp67Wf3HQrXanujSM=", "value": "<current value>" }
```

Here's an example of checking whether or not a conditional removal was successful:

```python
etag = db.child("users").child("Morty").get_etag()
response = db.child("users").child("Morty").conditional_remove(etag["ETag"])
if type(response) is dict and "ETag" in response:
    etag = response["ETag"] # our ETag was out-of-date
else:
    print("We removed the data successfully!")
```

Here's an example of looping to increase age by 1:

```python
etag = db.child("users").child("Morty").child("age").get_etag()
while type(etag) is dict and "ETag" in etag:
    new_age = etag["value"] + 1
    etag = db.child("users").child("Morty").child("age").conditional_set(new_age, etag["ETag"])
```

### Retrieve Data

#### val

Queries return a PyreResponse object. Calling `val()` on these objects returns the query data.

```
users = db.child("users").get()
print(users.val()) # {"Morty": {"name": "Mortimer 'Morty' Smith"}, "Rick": {"name": "Rick Sanchez"}}
```

#### key

Calling `key()` returns the key for the query data.

```
user = db.child("users").get()
print(user.key()) # users
```

#### each

Returns a list of objects on each of which you can call `val()` and `key()`.

```
all_users = db.child("users").get()
for user in all_users.each():
    print(user.key()) # Morty
    print(user.val()) # {"name": "Mortimer 'Morty' Smith"}
```

#### get

To return data from a path simply call the `get()` method.

```python
all_users = db.child("users").get()
```

#### shallow

To return just the keys at a particular path use the `shallow()` method.

```python
all_user_ids = db.child("users").shallow().get()
```

Note: `shallow()` can not be used in conjunction with any complex queries.

#### streaming

You can listen to live changes to your data with the `stream()` method.

```python
def stream_handler(message):
    print(message["event"]) # put
    print(message["path"]) # /-K7yGTTEp7O549EzTYtI
    print(message["data"]) # {'title': 'empyrebase', "body": "etc..."}

my_stream = db.child("posts").stream(stream_handler)
```

You should at least handle `put` and `patch` events. Refer to ["Streaming from the REST API"][streaming] for details.

[streaming]: https://firebase.google.com/docs/reference/rest/database/#section-streaming

You can also add a `stream_id` to help you identify a stream if you have multiple running:

```
my_stream = db.child("posts").stream(stream_handler, stream_id="new_posts")
```

#### close the stream

```python
my_stream.close()
```

#### Update the auth token mid stream

```python
def token_refresher():
    return your_auth_token # Implement a way to actually update your_auth_token using auth.refresh() outside this function.

def stream_handler(message):
    print(message["event"]) # put
    print(message["path"]) # /-K7yGTTEp7O549EzTYtI
    print(message["data"]) # {'title': 'empyrebase', "body": "etc..."}

my_stream = db.child("posts").stream(stream_handler, token="your_auth_token", token_refreshable=True, token_refresher=token_refresher, max_retries=3) # max_retries is optional and defaults to 3. Maximum retries to reauth stream before an exception is raised.
```

### Complex Queries

Queries can be built by chaining multiple query parameters together.

```python
users_by_name = db.child("users").order_by_child("name").limit_to_first(3).get()
```

This query will return the first three users ordered by name.

#### order_by_child

We begin any complex query with `order_by_child()`.

```python
users_by_name = db.child("users").order_by_child("name").get()
```

This query will return users ordered by name.

#### equal_to

Return data with a specific value.

```python
users_by_score = db.child("users").order_by_child("score").equal_to(10).get()
```

This query will return users with a score of 10.

#### start_at and end_at

Specify a range in your data.

```python
users_by_score = db.child("users").order_by_child("score").start_at(3).end_at(10).get()
```

This query returns users ordered by score and with a score between 3 and 10.

#### limit_to_first and limit_to_last

Limits data returned.

```python
users_by_score = db.child("users").order_by_child("score").limit_to_first(5).get()
```

This query returns the first five users ordered by score.

#### order_by_key

When using `order_by_key()` to sort your data, data is returned in ascending order by key.

```python
users_by_key = db.child("users").order_by_key().get()
```

#### order_by_value

When using `order_by_value()`, children are ordered by their value.

```python
users_by_value = db.child("users").order_by_value().get()
```

## Storage

The storage service allows you to upload images to Firebase.

### child

Just like with the Database service, you can build paths to your data with the Storage service.

```python
storage.child("images/example.jpg")
```

### put

The put method takes the path to the local file and an optional user token.

```python
storage = firebase.storage()
# as admin
storage.child("images/example.jpg").put("example2.jpg")
# as user
storage.child("images/example.jpg").put("example2.jpg", user['idToken'])
```

### download

The download method takes the path to the saved database file and the name you want the downloaded file to have.

```
storage.child("images/example.jpg").download("downloaded.jpg")
```

### get_url

The get_url method takes the path to the saved database file and user token which returns the storage url.

```
storage.child("images/example.jpg").get_url(user["idToken"])
# https://firebasestorage.googleapis.com/v0/b/storage-url.appspot.com/o/images%2Fexample.jpg?alt=media
```

### delete

The delete method takes the path to the saved database file and user token.

```
storage.delete("images/example.jpg",user["idToken"])
```

### Helper Methods

#### generate_key

`db.generate_key()` is an implementation of Firebase's [key generation algorithm](https://www.firebase.com/blog/2015-02-11-firebase-unique-identifiers.html).

See multi-location updates for a potential use case.

#### sort

Sometimes we might want to sort our data multiple times. For example, we might want to retrieve all articles written between a
certain date then sort those articles based on the number of likes.

Currently the REST API only allows us to sort our data once, so the `sort()` method bridges this gap.

```python
articles = db.child("articles").order_by_child("date").start_at(startDate).end_at(endDate).get()
articles_by_likes = db.sort(articles, "likes")
```

### Common Errors

#### Index not defined

+Indexing is [not enabled](https://firebase.google.com/docs/database/security/indexing-data) for the database reference.

## Firestore

The `firestore` method in empyrebase allows interaction with Firebase Firestore.

### Migration Notice (v2.0.0)

- `firebase_path` argument in `firestore()` has been deprecated and removed.  
- Firestore navigation now supports **chained `collection()` and `document()` methods**.
- Queries are now built using `where()`, `order_by()`, and `limit()` on collection references.
- If you used `firebase.firestore(firebase_path=...)`, remove `firebase_path` and update your code to use chained collection/document navigation.

**Example Update:**

Old (v1.x):

```python
firestore = firebase.firestore(firebase_path="users")
user = firestore.get_document("user_id")
```

New (v2.0.0):

```python
firestore = firebase.firestore()
user = firestore.collection("users").get_document("user_id")
```

### Initialize Firestore

Initialize Firestore with required project and authentication parameters.

```python
from empyrebase import Firestore

firebase_path = "your_firestore_path" # Optional. Base path for all Firestore operations. Defaults to "/"
auth_id = "your_auth_id_token" # Optional. Enables authorized transactions.
database_name = "your_database_name" # Optional. defaults to "(default)"


firestore = firebase.firestore(database_name=database_name, auth_id=auth_id)
```

**Note:** `firebase_path` in firestore initialization has been depracated since version 2.0.0.

### Authorization

Authorize Firestore using an authentication token. Firestore can be authorized at any time.

```python
firestore.authorize("auth_id_token")
```

### CRUD Operations

#### Navigation

Navigation can be done either using absolute paths using one of three methods:
1. `firestore.get_document("/path/to/document")`
2. Using chained collection-document pairs
3. Using path segments

Examples:
```python
collection1 = firestore.collection("path/to/collection")
collection2 = firestore.collection("path").document("to").collection("collection")
collection3 = firestore.collection("path", "to", "collection")
collection4 = firestore.collection("path/to", "collection")
document1 = collection1.get_document("document1")
document2 = collection1.document("document2").get_document()
document3 = collection2.document("path/to/document").get_document()
document4 = collection2.document("path", "to", "document")
```

The same logic applies to creating, updating, listing documents, and batch getting documents.

#### Create a Document

Creates a new document.

```python
data = {"name": "John Doe", "age": 30} # Optional
firestore.create_document("users/user_id", data)
# Alternatively, updating a non-existing document will create a new one.
firestore.create_document("users/user_id", data) # Data is required, but can be an empty dictionary
```

#### Retrieve a Document

Fetches a document.

```python
document = firestore.get_document("users/user_id")
print(document)
```

#### Batch Get Documents

Fetch multiple documents in one batch.

```python
documents = firestore.batch_get_documents(["users/user_id1", "users/user_id2"])
```

#### Run Query

Run a structured query against a collection. Methods:
- `where(field, op, value)`: Filters query
- `order_by(field, direction)`: Orders query based on field in ascending or descending order.
- `limit(lim)`: Limits results

Supported operators for filters:
|      Operator      |       API Value       |
|:------------------:|:---------------------:|
| ==                 | EQUAL                 |
| !=                 | NOT_EQUAL             |
| <                  | LESS_THAN             |
| <=                 | LESS_THAN_OR_EQUAL    |
| >                  | GREATER_THAN          |
| >=                 | GREATER_THAN_OR_EQUAL |
| array-contains     | ARRAY_CONTAINS        |
| in                 | IN                    |
| not-in             | NOT_IN                |
| array-contains-any | ARRAY_CONTAINS_ANY    |

```python
collection = firestore.collection("path/to/collection")
queried = collection.where("field", "==", "value").limit(10)
```

#### Update a Document

Update data in an existing document. If the document does not exist, it will be created with the new data.

```python
firestore.update_document("users/user_id", {"age": 31})
```

#### Delete a Document

Deletes a document.

```python
firestore.delete_document("users/user_id")
```

#### List Documents

Lists all documents in a collection.

```python
documents = firestore.list_documents("users")
```

#### Server timestamp

In order to get the server timestamp in a field value use `firestore.SERVER_TIMESTAMP`:

```python
data = {
    "name": "John Doe",
    "age": 30,
    "createdAt": firestore.SERVER_TIMESTAMP,
}
```
