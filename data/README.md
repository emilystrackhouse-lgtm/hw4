# Local data pack (not in Git)

Put the Campus Customs data pack here before starting the backend:

```text
hw4/data/campus_customs.db   the SQLite database (catalogue, inventory, users, chat_messages)
hw4/data/products/           the 102 product photos (.jpg), named as in catalogue.image_file_path
```

Then run `python ../prepare_product_images.py` from `backend/`, with the virtual environment active. It creates `data/products_web/`, white-background copies of the photos that the website shows. Everything in this folder except this README is ignored by Git.
