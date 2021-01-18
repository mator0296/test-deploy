from ..celery import app


@app.task
def check_payment_status():
    print("Status Checked---- call api {}".format("test"))
