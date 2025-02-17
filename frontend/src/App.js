import { useEffect, useState } from "react";
import "./App.css";

function App() {
  // use data to display the fetched transactions
  const [data, setData] = useState([]);
  const [groupBy, setGroupBy] = useState("");
  const [filters, setFilters] = useState({
    customer_id: "",
    item_id: "",
    date_range: {
      start: "",
      end: "",
    },
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    const requestBody = {};

    if (groupBy) {
      requestBody.group_by = groupBy;
    }

    if (filters.customer_id) {
      requestBody.customer_id = filters.customer_id;
    }
    if (filters.item_id) {
      requestBody.item_id = filters.item_id;
    }
    if (filters.date_range.start && filters.date_range.end) {
      requestBody.date_range = {
        start: filters.date_range.start,
        end: filters.date_range.end,
      };
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Failed to fetch data");
      }

      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [groupBy, filters]);

  const validateCustomerId = (value) => {
    return /^\d*$/.test(value); // Only allow digits
  };

  const validateItemId = (value) => {
    return /^\d*$/.test(value); // Only allow digits
  };

  const validateDateRange = (start, end) => {
    if (!start || !end) return true;
    return new Date(start) <= new Date(end);
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setError(null);

    // Validate input before updating state
    if (name === "customer_id" && !validateCustomerId(value)) {
      setError("Customer ID must be a number");
      return;
    }

    if (name === "item_id" && !validateItemId(value)) {
      setError("Item ID must be a number");
      return;
    }

    if (name.startsWith("date_")) {
      const dateKey = name === "date_start" ? "start" : "end";
      const newDateRange = {
        ...filters.date_range,
        [dateKey]: value,
      };

      if (!validateDateRange(newDateRange.start, newDateRange.end)) {
        setError("End date must be after start date");
        return;
      }

      setFilters((prev) => ({
        ...prev,
        date_range: newDateRange,
      }));
      return;
    }

    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="App">
      <h1>Transaction Analysis Dashboard</h1>

      {error && <div className="error-message">{error}</div>}

      <div className="controls">
        <div className="aggregation">
          <h3>Group By:</h3>
          <select value={groupBy} onChange={(e) => setGroupBy(e.target.value)}>
            <option value="">None</option>
            <option value="customer_id">Customer ID</option>
            <option value="item_id">Item ID</option>
            <option value="date">Date</option>
          </select>
        </div>

        <div className="filters">
          <h3>Filters:</h3>
          <input
            type="text"
            name="customer_id"
            placeholder="Customer ID"
            value={filters.customer_id}
            onChange={handleFilterChange}
          />
          <input
            type="text"
            name="item_id"
            placeholder="Item ID"
            value={filters.item_id}
            onChange={handleFilterChange}
          />
          <input
            type="date"
            name="date_start"
            value={filters.date_range.start}
            onChange={handleFilterChange}
          />
          <input
            type="date"
            name="date_end"
            value={filters.date_range.end}
            onChange={handleFilterChange}
          />
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <div className="results">
          <h2>Results</h2>
          {data.length === 0 ? (
            <p>No results found</p>
          ) : (
            <ul>
              {data.map((item, index) => (
                <li key={index}>
                  {groupBy === "customer_id" &&
                    `Customer ${item.customer_id}: Total Revenue $${item.total_revenue}`}
                  {groupBy === "item_id" &&
                    `Item ${item.item_id} (${item.name}): Total Quantity ${item.total_quantity}`}
                  {groupBy === "date" && `Date ${item.date}: Total Revenue $${item.total_revenue}`}
                  {!groupBy && `Transaction ${item.transaction_id}: $${item.total_amount}`}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
