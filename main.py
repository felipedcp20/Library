import os
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import  OAuth2PasswordRequestForm

from app.auth import authenticate_user, create_access_token, get_current_active_user, verify_role, get_password_hash
from app.models.token import Token
from app.models.database import Loan, User, Book
from app.dao import Dao


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


app = FastAPI()


@app.get("/", tags=["Root"])
async def version():
    return {"version": "1.0.0"}


@app.post("/token", tags=["Authentication"], response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/books/", tags=["Books"])
async def read_books():
    client = Dao()
    books = client.get_books()    
    return {"books": books}
    

@app.post("/books/loan", tags=["Books"])
async def loan_book(
    loan: Loan,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    loan.user_id = current_user.id
    client = Dao()
    try:
        quantity = client.get_quantity_books(loan.book_id)
        if quantity == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book not available",
                headers={"WWW-Authenticate": "Bearer"},
            )
        quantity -= 1

        client.update_quantity_books(loan.book_id, quantity)

        id_prestamo =  client.register_loan(loan)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating loan",
            headers={"WWW-Authenticate": "Bearer"},
        )    
    return {"message": f'the loan was created successfully with id {id_prestamo}'}


@app.post("/books/create", tags=["Admin"])
async def create_book(
    book: Book,
    current_user: Annotated[User, Depends(verify_role("admin"))],
):
    client = Dao()
    try: 
        client.create_book(book)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating book",
            headers={"WWW-Authenticate": "Bearer"},
        )
    message = f'the book {book.name} was created successfully'
    return {"message": message}


@app.delete("/books/delete/{book_id}", tags=["Admin"])
async def delete_book(
    book_id: int,
    current_user: Annotated[User, Depends(verify_role("admin"))],
):
    client = Dao()
    try: 
        client.delete_book(book_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting book",
            headers={"WWW-Authenticate": "Bearer"},
        )
    message = f'the book with id {book_id} was deleted successfully'
    return {"message": message}

@app.post("/books/return", tags=["Books"])
async def return_book(
    id_prestamo: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    client = Dao()
    try:
        if id_prestamo == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Loan not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        id_book = client.return_book(id_prestamo)
        quantity =  client.get_quantity_books(id_book)
        quantity += 1
        client.update_quantity_books(id_book, quantity)
    
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error returning book",
            headers={"WWW-Authenticate": "Bearer"},
        )    
    return {"message": f'the loan was returned successfully with id {id_prestamo}'}


@app.get("/books/loans", tags=["Books"])
async def read_loans(
    current_user: Annotated[User, Depends(get_current_active_user)],
    all : bool = False
):
    client = Dao()
    loans = client.get_loans(all , current_user.id)    
    return {"loans": loans}

@app.post("/users/create", tags=["Admin"])
async def create_user(
    user: User,
    current_user: Annotated[User, Depends(verify_role("admin"))],
):
    client = Dao()
    try: 
        user.password = get_password_hash(user.password)
        client.create_user(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    message = f'the user {user.username} was created successfully'
    return {"message": message}