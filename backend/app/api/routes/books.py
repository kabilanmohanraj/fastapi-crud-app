from enum import Enum
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from backend.app.models import Books, BookCreate, BookPublic, BookUpdate
from backend.app.core.db import SessionDep
from backend.app.api.dependencies import CurrentUser
from backend.app.shared_queue import SSEQueueDep

from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/books", tags=["books"])


@router.get(
    "/", response_model=list[BookPublic],
    summary="Retrieve a list of books with pagination.",
    responses={
        200: {"description": "Books retrieved successfully."},
        400: {"description": "Invalid pagination parameters."},
        401: {"description": "Unauthorized access."},
        500: {"description": "Internal server error."}
    }
)
async def get_books_with_pagination(session: SessionDep, current_user: CurrentUser, crud_event_queue: SSEQueueDep, skip: int = 0, limit: int = 10):
    """
    **Input Parameters (Query parameters)**: \n
    - `skip` (int): Number of books to skip (for pagination). Default is 0. \n
    - `limit` (int): Maximum number of books to retrieve. Default is 10. \n
    - Sample request: `/books?skip=10&limit=5` -> retrieves books 11 to 15. \n
    """
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters. Ensure 0 <= skip and 1 <= limit <= 100.")
    
    try:
        query = select(Books).offset(skip).limit(limit)
        books = session.exec(query).all()
        
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    await crud_event_queue.put(f"Fetched {len(books)} books. Displaying books {skip} to {skip + len(books) - 1}.")
    
    return books


@router.get(
    "/{book_id}",
    response_model=BookPublic,
    summary="Retrieve a specific book",
    description="Fetch a particular book using its ID.",
    responses={
        200: {"description": "Book found successfully."},
        401: {"description": "Unauthorized access."},
        404: {"description": "Book not found."},
        500: {"description": "Internal server error."},
    },
)
async def get_book_by_id(book_id: int, session: SessionDep, current_user: CurrentUser, crud_event_queue: SSEQueueDep):
    book = session.get(Books, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")
    
    await crud_event_queue.put(f"Book fetched: {book.title} by {book.author} (ID: {book_id})")
    
    return book


@router.post(
    "/",
    response_model=BookPublic,
    summary="Create a new book",
    description="Add a new book to the DB with details.",
    responses={
        200: {"description": "Book created successfully."},
        400: {"description": "Invalid input data."},
        401: {"description": "Unauthorized access."},
        500: {"description": "Internal server error."},
    },
)
async def create_book(book: BookCreate, session: SessionDep, current_user: CurrentUser, crud_event_queue: SSEQueueDep):
    try:
        new_book = Books(
            title=book.title,
            author=book.author,
            published_date=book.published_date,
            summary=book.summary,
            genre=book.genre.value
        )
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
        
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    await crud_event_queue.put(f"New book created: {new_book.title} by {new_book.author} (ID: {new_book.id})")
    
    return new_book


@router.put(
    "/{book_id}",
    response_model=BookPublic,
    summary="Update an existing book",
    description="Update details of a particular book given its ID.",
    responses={
        200: {"description": "Book updated successfully."},
        401: {"description": "Unauthorized access."},
        404: {"description": "Book not found."},
        500: {"description": "Internal server error."},
    },
)
async def update_book(book_id: int, book: BookUpdate, session: SessionDep, current_user: CurrentUser, crud_event_queue: SSEQueueDep):
    try:
        book_in_db = session.get(Books, book_id)
        if not book_in_db:
            raise HTTPException(status_code=404, detail="Book not found.")

        book_data = book.model_dump(exclude_unset=True)
        for field, value in book_data.items():
            if isinstance(value, Enum):
                value = value.value
            setattr(book_in_db, field, value)

        session.add(book_in_db)
        session.commit()
        session.refresh(book_in_db)
        
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    await crud_event_queue.put(f"Book updated: {book_in_db.title} by {book_in_db.author} (ID: {book_id})")

    return book_in_db


@router.delete(
    "/{book_id}",
    response_model=BookPublic,
    summary="Delete a book",
    description="Remove a book from the system given its ID.",
    responses={
        200: {"description": "Book deleted successfully."},
        401: {"description": "Unauthorized access."},
        404: {"description": "Book not found."},
        500: {"description": "Internal server error."},
    },
)
async def delete_book(book_id: int, session: SessionDep, current_user: CurrentUser, crud_event_queue: SSEQueueDep):
    try:
        book = session.get(Books, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found.")
        
        session.delete(book)
        session.commit()
        
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    await crud_event_queue.put(f"Book deleted: {book.title} by {book.author} (ID: {book_id})")

    return book
