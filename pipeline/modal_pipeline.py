from dagster import op, job, repository, Out, Output
from database.tursodb import get_connection
import modal

app = modal.App(
    image=modal.Image.debian_slim().pip_install("dagster", "libsql_experimental")
)

@app.function()
@modal.batched(max_batch_size=100, wait_ms=1000)
def process_batch(batch):
    results = []
    for row in batch:
        # Perform operations on the row
        print(row)
        results.append(row)  # Append the processed row to results
    return results  # Return the list of processed rows

@op(out=Out(list))
def query_products_from_db(_):
    conn = get_connection()
    results = conn.execute("SELECT * FROM products").fetchall()

    # Create batches of a suitable size (e.g., 100)
    batch_size = 100
    batched_results = [results[i:i+batch_size] for i in range(0, len(results), batch_size)]

    return Output(batched_results)

@op
def process_batches(batched_results):
    # Create a list to store deferred tasks
    deferred_tasks = []

    for batch in batched_results:
        # Process each batch asynchronously using Modal Labs
        with app.run():
            batch_tasks = process_batch._call_function([batch], {})
            if isinstance(batch_tasks, tuple):
                batch_tasks = list(batch_tasks)  # Convert tuple to list if necessary
            deferred_tasks.extend(batch_tasks)  # Append all tasks to deferred_tasks

    # Wait for all deferred tasks to complete
    for task in deferred_tasks:
        if hasattr(task, 'result'):
            task.result()

@job
def my_pipeline():
    batched_results = query_products_from_db()
    process_batches(batched_results)

@repository
def my_repository():
    return [my_pipeline]