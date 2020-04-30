# Horse Racing Model

This started as a quick test of a mates wagering strategy and turned into a larger project.
The goal is to create a webapp which allows a user to see any optimal wagers which might be available.
Currently I am populating a MySQL database with information, trying to normalise the data as much as possible.

###Stage One: Collecting from one data source.
This was where I learnt that any data which can be viewed on the internet can be collected and downloaded.
I chose to start with tab.com.au because they have the greatest retail presence in Australia and their webpage was straight forward to scrape.
Main Problem encountered: How should I store the information that I downloaded?
Chosen Solution: Store as a very raw JSON. I chose this because I assumed that I wouldn't be doing much with the info except for testing a friends wagering strategy. In hindsight this was a really bad way to store the data.

###Stage Two: Test my mates wagering strategy.
This was where I got to test some of the optimisation strategies that I struggled with at Uni. I decided just to run my mates strategy and see how it performed, grouped by day and venue, over the past year. Turns out that their strategy was probably coming out at almost exactly break even. The big catch was that they were limited in maximum wager.
Main problem: Strategy depended on data I didn't have.
Chosen Solution: Build a database and a front end so I can add my own information.

##Current Stage
###Stage Three: Construct a database. 
Using the MySQL connector and MySQL I built out a database slowly, starting with a mess of many to many relationships and slowly resolving them. 
Main Problem: Data format for scraped data is quite difficult to work with/
Chosen Solution: Just iterate over the poor data and insert it into the tables. This needs a refactor before I move onto collecting extra data.
