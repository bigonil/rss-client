# Azure Status RSS Client

A lightweight FastAPI web app that reads and displays updates from an RSS feed — specifically designed to track [Azure Status](https://status.azure.com). The app is containerized using Docker and ready for deployment on **Azure Container Apps**.

---

## 🚀 Features

- Parses and displays any standard RSS feed (default: Azure status feed).
- Simple, clean interface rendered with Jinja2.
- Python FastAPI backend for speed and modernity.
- Dockerized for easy cloud deployment (Azure-ready).
- Gracefully handles empty or inactive feeds.

---

## 🖼 Example UI

When Azure has no active status updates, the app shows:

> **"No current incidents or status updates."**

---
