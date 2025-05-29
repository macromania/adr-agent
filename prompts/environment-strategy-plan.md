# Environment Strategy Prompt

DON'T CHANGE THIS FILE DURING EDITS.

## Context

 What is the purpose of this section?

- Convience reader why this is a modern software engineering and Devops.
- Convience reader why this will have positive impact on the business.
- Convience reader why this is for improving the developer experience and velocity of product.

## Current State

ASK CLARIFIYING QUESTIONS BEFORE WRITING THIS SECTION.

What is the purpose of this section?

- To provide an overview of the current state
- To highlight the need for a strategy
- To highlight the shotcomings of the current state

## Task

Create a strategy document for managing the multiple environments deploying customer software in Azure. The strategy document will include the following sections:

- Context, Decision Drivers, Considered Options, Decision Outcome, Pros and Cons of the Chosen Option.
- Context: This section will provide an overview of the current context and the need for an environment strategy.
- Current State: This section will outline the current state of the environments, including any challenges or limitations that exist. ASK CLARIFYING QUESTIONS BEFORE WRITING THIS SECTION.
- Decision Drivers: This section will outline the key factors that influenced the decision-making process, such as cost, security, developer experience and any other pain points provided in Current State.
- Considered Options: This section will list the different options that were considered for managing the environments, including their pros and cons.
- Decision Outcome: This section will summarize the chosen option and the reasons for its selection.
- Pros and Cons: This section will provide a detailed analysis of the pros and cons of the chosen option, including any potential risks or challenges that may arise during implementation.
- Keep track of the progress of each section and visualise the progress with a simple table in the output.
- ASK CLARIFYING QUESTIONS WHERE NEEDED UNTIL YOU FINISH ALL SECTIONS.

## Writing Guidelines

- The strategy will be written in a clear and concise manner, using bullet points and headings to organize the information.
- The strategy will be reviewed and approved by the relevant stakeholders before implementation.
- The strategy will be communicated to all relevant teams. Product, Infrastructure, Netwkring and individuals involved in the management of the Azure environments.

## Styling Guidelines

- Use markdown formatting for headings, bullet points, and code blocks.
- Create tables in markdown with correct indentation and clearer visibility.
- Provide list of references used in the strategy, such as links to Azure documentation, best practices, and any other relevant resources at the bottom of the document in a "References" section.

## Engineering Guidelines

- Provide clear naming conventions for the environments, such as "DEV", "TEST", "UAT", "PROD".
- Provide clear naming conventions for the relevant Azure subscriptions, such as "DEV-Subscription", "TEST-Subscription", "UAT-Subscription", "PROD-Subscription".
- Make sure Production environments, UAT and PROD is in relevant Azure Tenant. ASK CLARIFYING QUESTIONS BEFORE WRITING THIS SECTION.
- Make sure the process and steps taken to create these environments can be applied to Production environment as well.
- Make sure the Production process needs to be conducted by customer team who has Production access. Microsoft team will not have access to Production environment.
- Make sure use of Github Actions, Github Environments, Github Environment Protection Rules and Github Environment Approval Rules are used to manage the environments except DEV. 
- Make sure DEV will be automatically deployed by the CI/CD pipeline from the main branch.

## Output Guidelines

- Crate a markdown file with the name `environment-strategy.md` in the `/outputs` directory.
- Don't change anything in the `.github` directory or the `/prompts` directory.
