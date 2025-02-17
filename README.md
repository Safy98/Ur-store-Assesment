# My Approach for this solution:

## Front-end:

### Requirments:
- the user can request the data from the back-end in 3 forms:
    1. customers revenue
    2. items sales
    3. total revenue over a period of time

- the user can filter the data from the back-end in 3 forms:
    1. by customer id
    2. by itms id
    3. by applying a time period

- the reult should change when ever a filter is applied or an aggregation method has changed

### the solution:

- I classified the changes in 2 categories:
    1. filters 
    2. aggregation

- those two changes are represented in the code as a state and are listened by a useEffect.
- when ever a filter or a group-by input change, thier state will change by an onChange method.
- when ever  a filter or a group-by state change the useEffect will trigger and call an async function which will collect the data, validate it , POST it to the endpoint and recieve the new results and set the value of the result in the data State whcih will cause the data value to change in each place it presents.

## Back-end:

