# Corey-Schafer-Tutorial
Here im goning to be tracking my progress with that FastAPI tutorial, implementing JWT was harder than i thought, so, i hope i can learn from that tutorial, i'll be following it from the start, maybe i can learn new things too

## 19/08/2026
### What did i learn?
1.  There's a new way to create a "Base" class and use it in our `models.py`
Old way: 
```python
Base = declarative_base()
```
New way: 
```python
class Base(DeclarativeBase):
    pass
```
2. I learned how to create table relationships properly with the `ForeignKey` module from `sqlalchemy` and the `relationship` module from `sqlalchemy.orm`

3. There's a better way to make the queries from the database. If you want to query a user from the database, instead of doing something like:
```python
user = db.query(models.User).filter(models.User.id == id).first()
```
You'll need to import `select` from `sqlalchemy` and then:
```python
user = db.execute(select(models.User).where(models.User.id == id).scalars().first())
```

I also made comments in the code.



