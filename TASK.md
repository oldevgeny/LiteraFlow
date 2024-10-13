# Test Assignment

### Stack

	• Python
	• aiohttp
	• PostgreSQL
	• SQLAlchemy

### Description
We are developing an API service that will provide users with access to various literary works.

### Requirements

	• The book file can be stored at your discretion.
	• Create data structures in the database that will allow future access to books by name, author, date_published, and genre.
	• Develop create/read endpoints that allow users to:
	• Upload books.
	• Retrieve a list of books filtered by one of the parameters (name, author, date_published, genre).
	• Access a specific book by its id (the book can be downloaded or viewed online).
	• For the create endpoint, add validation to ensure that the user has provided the mandatory fields (name, author, date_published).
	• Database queries should be asynchronous.

### Implementation

	• Create a repository on GitLab/GitHub and upload your code there.
	• Functions should be properly annotated.
	• The API should be covered by tests.
	• Bonus points for adding Docker support to allow the application to run locally, along with instructions.

### Additional Functionality (Optional)
**Task Extension:**

	• Add an endpoint to accept and parse an XLS file (a sample file example is media/decline_list_example.xlsx) that contains two sheets: name and author.
	• The first sheet contains the name of the book.
	• The second sheet contains the author of the book.
	• This file is sent by a publishing house and contains references to books that should be included in a denied list—meaning they become unavailable for download but remain available for viewing.