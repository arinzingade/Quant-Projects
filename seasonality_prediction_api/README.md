
# Quant-Projects: Supply API Forecasting

This repository contains a Dockerized API for forecasting based on time-series data. The API utilizes the SARIMA model to predict future values based on historical input data.

## Project Setup

### Prerequisites

1. **Docker**: You will need Docker installed to run the application inside containers.
   - Install Docker from [here](https://www.docker.com/get-started).
   - Verify installation with:
     ```bash
     docker --version
     ```

### Step-by-Step Instructions

#### Step 1: Clone the Repository

Clone the `Quant-Projects` repository to your local machine.

```bash
git clone https://github.com/arinzingade/Quant-Projects.git
```

#### Step 2: Navigate to the `supply_api` Directory

After cloning the repository, navigate to the `supply_api` folder.

```bash
cd Quant-Projects/supply_api
```

#### Step 3: Build and Run the Docker Container

Use `docker-compose` to build and run the application inside a container. This will also set up the necessary dependencies for running the forecasting API.

```bash
docker-compose up --build
```

The API will start running on port `8000` by default.

#### Step 4: Send a Forecast Request

Once the container is running, you can send a POST request to `http://127.0.0.1:8000/forecast` with the following JSON payload. This payload includes the input data (`dates`, `pre_prepared`, `consumption`) and the SARIMA parameters used for forecasting.

##### Sample JSON Payload

```json
{
    "data": {
        "dates": [
            "2023-10-01", "2023-10-02", "2023-10-03", "2023-10-04", "2023-10-05",
            "2023-10-06", "2023-10-07", "2023-10-08", "2023-10-09", "2023-10-10",
            "2023-10-11", "2023-10-12", "2023-10-13", "2023-10-14", "2023-10-15",
            "2023-10-16", "2023-10-17", "2023-10-18", "2023-10-19", "2023-10-20",
            "2023-10-21", "2023-10-22", "2023-10-23", "2023-10-24", "2023-10-25",
            "2023-10-26", "2023-10-27", "2023-10-28", "2023-10-29", "2023-10-30",
            "2023-10-31"
        ],
        "pre_prepared": [
            150, 100, 120, 110, 90, 130, 160, 180, 90, 110, 100,
            120, 130, 140, 200, 110, 95, 105, 115, 125, 135, 190, 
            85, 95, 105, 115, 125, 150, 170, 100, 110
        ],
        "consumption": [
            20, 30, 25, 15, 10, 50, 40, 30, 20, 15, 20, 35, 45, 25, 50,
            20, 10, 15, 20, 30, 40, 60, 15, 10, 20, 25, 35, 45, 50, 20, 15
        ]
    },
    "params": {
        "forecast_steps": 10,
        "sarima_order": [1, 1, 1],
        "seasonal_order": [1, 1, 1, 7]
    }
}
```

### API Response

Upon a successful request, the API will return the forecasted values along with confidence intervals and any relevant information for your forecasting needs.

```json
{
    "forecast_dates": [
        "2023-11-01",
        "2023-11-02",
        "2023-11-03",
        "2023-11-04",
        "2023-11-05",
        "2023-11-06",
        "2023-11-07",
        "2023-11-08",
        "2023-11-09",
        "2023-11-10"
    ],
    "original_forecast": [
        104.88333750421857,
        111.89537237189853,
        126.7541339036307,
        150.61159090700954,
        172.185377098379,
        99.52467845487087,
        109.85766160482102,
        105.9133236067632,
        110.42849689603486,
        127.78430584003763
    ],
    "optimized_forecast": [
        104.88333750421857,
        111.89537237189853,
        126.7541339036307,
        150.61159090700954,
        172.185377098379,
        99.52467845487087,
        109.85766160482102,
        105.9133236067632,
        110.42849689603486,
        127.78430584003763
    ],
    "confidence_intervals": [
        {
            "lower": 76.67388228258655,
            "upper": 133.0927927258506
        },
        {
            "lower": 83.72308865586926,
            "upper": 140.06765608792782
        },
        {
            "lower": 98.54882918017671,
            "upper": 154.9594386270847
        },
        {
            "lower": 122.44494114167722,
            "upper": 178.77824067234187
        },
        {
            "lower": 144.0160912439811,
            "upper": 200.35466295277692
        },
        {
            "lower": 71.35540682169815,
            "upper": 127.69395008804358
        },
        {
            "lower": 81.68838506772745,
            "upper": 138.0269381419146
        },
        {
            "lower": 71.48122731929881,
            "upper": 140.34541989422758
        },
        {
            "lower": 76.13937053694117,
            "upper": 144.71762325512856
        },
        {
            "lower": 93.46153855924466,
            "upper": 162.1070731208306
        }
    ]
}
```

---


### Troubleshooting

- **Docker Not Running**: Ensure Docker is installed and running properly. If the container fails to start, use `docker logs <container_id>` to check for any error messages.
- **API Response Errors**: If the API does not respond as expected, check the request format and ensure the payload matches the required structure.
