# ☀️ Solar Energy Monitoring API

> Serverless GraphQL API for monitoring solar energy stations across the USA.  
> Built with **AWS Chalice**, **GraphQL (Strawberry)**, **DynamoDB**, and **LocalStack**.

---

## 🏗️ Architecture

```
Client (Postman / Frontend)
         │
         ▼  HTTP POST /graphql
   API Gateway  ◄── auto-created by Chalice
         │
         ▼
   AWS Lambda (app.py)
         │
         ▼
      DynamoDB
   ┌────────────────────┐
   │ SolarSites         │
   │ EnergyReadings     │
   └────────────────────┘

S3 Bucket (solar-readings)
         │  CSV uploaded
         ▼
   AWS Lambda  ◄── S3 event trigger
   csv_processor.py
         │
         ▼
      DynamoDB (EnergyReadings)

AWS EventBridge
         │  every hour (cron)
         ▼
   AWS Lambda
   aggregate_metrics()
         │
         ▼
   Console logs with metrics summary
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| [AWS Chalice](https://github.com/aws/chalice) | Python serverless framework — deploys Lambda + API Gateway automatically |
| [Strawberry](https://strawberry.rocks/) | GraphQL library for Python |
| [DynamoDB](https://aws.amazon.com/dynamodb/) | NoSQL database |
| [S3](https://aws.amazon.com/s3/) | CSV file storage |
| [LocalStack](https://localstack.cloud/) | Local AWS emulator for development |
| [GitHub Actions](https://github.com/features/actions) | CI/CD pipeline |

---

## 📁 Project Structure

```
solar-api/
├── .chalice/
│   └── config.json           # Chalice config: app name, stages, env vars
├── .github/
│   └── workflows/
│       └── deploy.yml        # CI/CD pipeline
├── chalicelib/
│   ├── __init__.py
│   ├── models.py             # DynamoDB operations (get/create/query)
│   ├── schema.py             # GraphQL types: SolarSite, EnergyReading
│   ├── resolvers.py          # GraphQL Query & Mutation resolvers
│   └── csv_processor.py      # S3 CSV file parser
├── app.py                    # Main entrypoint: routes, S3 trigger, cron
├── test-readings.csv         # Sample CSV for local testing
└── requirements.txt
```

---

## 🚀 Local Development

### Prerequisites

- Python 3.9+
- Docker (for LocalStack)
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Zahumennov/solar-api.git
cd solar-api
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start LocalStack

```bash
docker run --rm -p 4566:4566 localstack/localstack:3.0.0
```

Wait for `Ready.` message.

### 5. Create DynamoDB tables

Open a **new terminal tab** and run:

```bash
awslocal dynamodb create-table \
  --table-name SolarSites \
  --attribute-definitions AttributeName=site_id,AttributeType=S \
  --key-schema AttributeName=site_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1 \
  --endpoint-url http://localhost:4566

awslocal dynamodb create-table \
  --table-name EnergyReadings \
  --attribute-definitions AttributeName=site_id,AttributeType=S AttributeName=timestamp,AttributeType=S \
  --key-schema AttributeName=site_id,KeyType=HASH AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1 \
  --endpoint-url http://localhost:4566
```

### 6. Create S3 bucket

```bash
awslocal s3 mb s3://solar-readings \
  --region us-east-1 \
  --endpoint-url http://localhost:4566
```

### 7. Start the API

```bash
chalice local
```

API is now running at `http://127.0.0.1:8000` 🎉

---

## 🧪 Testing

### Create a solar site

```bash
curl -X POST http://127.0.0.1:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { createSite(input: { name: \"Solar Farm Kyiv\", location: \"Kyiv\", capacity: 500.0 }) { siteId name location capacity createdAt } }"}'
```

### Get all sites

```bash
curl -X POST http://127.0.0.1:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ sites { siteId name location capacity } }"}'
```

### Add a reading manually

```bash
curl -X POST http://127.0.0.1:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { addReading(input: { siteId: \"YOUR_SITE_ID\", outputKw: 245.5 }) { siteId timestamp outputKw } }"}'
```

### Get readings for a site

```bash
curl -X POST http://127.0.0.1:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ readings(siteId: \"YOUR_SITE_ID\", limit: 10) { timestamp outputKw } }"}'
```

### Upload CSV to S3

```bash
awslocal s3 cp test-readings.csv s3://solar-readings/test-readings.csv \
  --endpoint-url http://localhost:4566
```

### Process CSV manually

> ⚠️ S3 event triggers are not supported in `chalice local` mode. Run the processor directly:

```bash
python3 -c "
from chalicelib.csv_processor import process_csv
result = process_csv('solar-readings', 'test-readings.csv')
print(result)
"
```

---

## 📊 GraphQL Schema

### Types

```graphql
type SolarSite {
  siteId: ID!
  name: String!
  location: String!
  capacity: Float!
  createdAt: String!
}

type EnergyReading {
  siteId: ID!
  timestamp: String!
  outputKw: Float!
}
```

### Queries

```graphql
# Get all sites
query {
  sites {
    siteId
    name
    location
    capacity
  }
}

# Get single site by ID
query {
  site(siteId: "abc-123") {
    name
    location
    capacity
  }
}

# Get readings for a site (latest 10 by default)
query {
  readings(siteId: "abc-123", limit: 10) {
    timestamp
    outputKw
  }
}
```

### Mutations

```graphql
# Create a new site
mutation {
  createSite(input: {
    name: "Solar Farm Kyiv"
    location: "Kyiv"
    capacity: 500.0
  }) {
    siteId
    name
    createdAt
  }
}

# Add a sensor reading
mutation {
  addReading(input: {
    siteId: "abc-123"
    outputKw: 245.5
  }) {
    timestamp
    outputKw
  }
}
```

---

## ⚙️ Automated Workflows

### S3 CSV Processor

When a `.csv` file is uploaded to the `solar-readings` S3 bucket, a Lambda function automatically parses it and saves all readings to DynamoDB.

Expected CSV format:

```
site_id,output_kw,timestamp
abc-123,245.5,2026-04-07T10:00:00
abc-123,312.0,2026-04-07T11:00:00
abc-456,180.3,2026-04-07T10:00:00
```

### Hourly Metrics Aggregation

A scheduled Lambda runs every hour and logs for each site:

- ☀️ Total output (kW)
- 📊 Average output (kW)
- ⚡ Maximum output (kW)

---

## 📝 Notes

- DynamoDB stores `capacity` and `output_kw` as strings internally (DynamoDB limitation with floats) and converts them back to `float` in resolvers.
- LocalStack data is **not persisted** between Docker restarts — re-create tables and data after each restart.
- `chalice local` does not support S3 event triggers — use the manual Python call for local testing.
