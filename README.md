# Smart Buyer - Backend 🛒

Welcome to the Smart Buyer backend repository! This repository houses the server-side components of an innovative grocery shopping companion, Smart Buyer. The mission is to help users make smarter shopping choices and optimize their grocery spending. 🚀

## Overview 🌟

Smart Buyer is designed to streamline the grocery shopping experience by identifying the most cost-effective stores for your specific shopping cart. With this intelligent platform, users can effortlessly create customized shopping lists, compare prices across multiple stores, and make informed decisions to save on grocery bills.

Visit the website: [www.besmartbuyers.com](https://www.besmartbuyers.com) 🌐

## Technologies 🧰

- **Language:** Python 🐍
- **Framework:** Flask 🌐
- **Database:** PostgreSQL 🐘
- **Containerization:** Docker 🐳
- **Web Scraping:** Selenium 🤖
- **Hosting:** Heroku (PaaS) 🚢

## Key Features 🎯

- **Custom Shopping Lists:** Create and manage shopping lists tailored to your needs. 📋
- **Price Comparison:** Compare prices from different stores for items in your cart. 💲
- **Real-time Updates:** Automated data updates every 24 hours for accurate pricing information from major supermarket chains in Israel. 🔄
- **Seamless Communication:** A custom communication protocol ensures smooth frontend-backend interaction. 📡

## Automated Data Scraping 🤖

The backend performs automated data scraping from major supermarket chains' websites in Israel. According to Israeli law since 2016, these supermarkets are required to share their pricing data online, often in XML files. The scraping agents run every 24 hours to collect and update the pricing information, ensuring that users always have access to the most current prices. 🌐
The database contains a vast amount of product data, with over 6 million products, making Smart Buyer one of the most comprehensive sources for grocery price comparison.
Selenium, a powerful web automation tool, is used to navigate and extract data from the websites, providing a robust and reliable scraping solution.

## Getting Started 🚀

To set up the backend locally, follow these steps:

1. Clone this repository to your local machine. 📦
2. Install the required dependencies by running `pip install -r requirements.txt`. 🛠️
3. Set up a PostgreSQL database and configure the connection in the `config.py` file. 🏢
4. Run the Flask application using `python run.py`. 🚀

## Hosting and Deployment ☁️

The backend is hosted on Heroku, a robust cloud platform. Automated data updates are scheduled to keep the information up-to-date. AWS Route 53 is used for domain management, and AWS Amplify is used for frontend hosting and cloud services. 🌐
