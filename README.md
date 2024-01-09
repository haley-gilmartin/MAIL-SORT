## MAIL-SORT
Sorts, recalls, deletes, and manages email on command using OpenAI.

### Assignments

[ DUE ] Jan 3, 2024
See task 1 below
I need you to make the code more efficient and to finish the features listed. I will aid in this and answer questions as needed. Feel free to schedule face time meetings

### Project Overview, Tasks, and Notes

1.  Framework

Sending, drafting, creating labels, searching, adding labels, (threads if necessary), deleting emails

3. Data Storage

Look into Redis software and vector storage. reference DCUBE for pipelining

4. AI application

This is the fun and easy part

5. AI UI application

I'm thinking of making it into a downloadable google playstore extension. that would be sick.

#### Notes
Huge mess rn. huge mess.
Not that that easy of a project like I had anticipated. 
i forgot about the sheer magnitude of data we'll be working with because most people are email pigs
please please please don't make it so i have a $500 OpenAI bill. 
we need to use vectors and/or langchain to cut costs and code for efficiency of data recall
(do we actually though? I need to create a detailed outline to really breakdown how this is going to work)


On the topic of vector processing:

https://platform.openai.com/docs/guides/embeddings/what-are-embeddings

Read emails as they come in : AI Feed (Topic, intentions, type, people) > Vector storage. <--- that query list needs some futher consideration

Recall: 
1. Keyword extraction > GMail API search function > vector matching
2. Vector matching by date (whole database) and other metadata
3. (generate better ideas because those aren't great ngl)

Need a good vector comparison algorithm (see cse 20 notes) or possibly provided by openai or another source?


#### Tasks

1. clean up code + finish framework
2. organize into file hierarchy 
3. Data storage + reorganize
4. AI application + clean up
5. UI Research
6. UI execution
7. Reevaluate intentions for project (are we actually doing something with it or is it just a personal assistant just for us)



# SET UP
1. Add kumar to auth google cloud + git
2. Environment variables + API key
3. Run quickstart.py + troubleshoot 
4. Installs (dotenv, gmail api, etc.)
5. Walk through + token.json
6. Assignment overview
