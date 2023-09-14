# YooCard backend

### Deployment
```bash
git clone https://github.com/Kryspinoff/YooCard-Backend
cd YooCard-Backend/
```

Create and activate the virtual environment and then install all dependencies from the requirements.txt.
Then configure the `.env.dev` file.

Run the following code to start the services:

```bash
uvicorn app.main:app --port 8000
```