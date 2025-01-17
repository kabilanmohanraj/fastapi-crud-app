from fastapi import APIRouter, HTTPException
from sqlmodel import select

from backend.app.models import Books, BookCreate, BookPublic, BookUpdate
from backend.app.core.db import SessionDep
from backend.app.api.dependencies import CurrentUser
from backend.app.shared_queue import SSEQueueDep

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[BookPublic])
async def get_books(session: SessionDep, current_user: CurrentUser, crud_event_queue: SSEQueueDep, skip: int = 0, limit: int = 10):
    """
    Retrieve a list of books with pagination.
    
    **Input Parameters**:
    - `skip` (int): Number of books to skip (for pagination). Default is 0.
    - `limit` (int): Maximum number of books to retrieve. Default is 10.
    """
    
    query = select(Books).offset(skip).limit(limit)
    books = session.exec(query).all()
    
    await crud_event_queue.put(f"Fetched {len(books)} books. Displaying books {skip} to {skip + limit-1}.")
    
    return books


@router.get(
    "/{book_id}",
    response_model=BookPublic,
    summary="Retrieve a specific book",
    description="Fetch a particular book using its ID.",
    responses={
        200: {"description": "Book found and returned successfully."},
        404: {"description": "Book not found."},
    },
)
async def get_book(book_id: int, session: SessionDep, current_user: CurrentUser, crud_event_queue: SSEQueueDep):
    
    book = session.get(Books, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    await crud_event_queue.put(f"Book read: {book.title} by {book.author} (ID: {book_id})")
    
    return book


@router.post(
    "/",
    response_model=BookPublic,
    summary="Create a new book",
    description="Add a new book to the DB with details.",
    responses={
        200: {"description": "Book created successfully."},
    },
)
async def create_book(book: BookCreate, session: SessionDep, current_user: CurrentUser, crud_event_queue: SSEQueueDep):
    new_book = Books(
        title=book.title,
        author=book.author,
        published_date=book.published_date,
        summary=book.summary,
        genre=book.genre
    )
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    
    await crud_event_queue.put(f"New book created: {new_book.title} by {new_book.author} (ID: {new_book.id})")
    
    return new_book


@router.put(
    "/{book_id}",
    response_model=BookPublic,
    summary="Update an existing book",
    description="Update details of a particular book given its ID.",
    responses={
        200: {"description": "Book updated successfully."},
        404: {"description": "Book not found."},
    },
)
async def update_book(book_id: int, book: BookUpdate, session: SessionDep, current_user: CurrentUser, crud_event_queue: SSEQueueDep):
    book_in_db = session.get(Books, book_id)
    if not book_in_db:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book_data = book.model_dump(exclude_unset=True)
    book_in_db.sqlmodel_update(book_data)
    session.add(book_in_db)
    session.commit()
    session.refresh(book_in_db)
    
    await crud_event_queue.put(f"Book updated: {book_in_db.title} by {book_in_db.author} (ID: {book_id})")
    
    return book_in_db


@router.delete(
    "/{book_id}",
    response_model=BookPublic,
    summary="Delete a book",
    description="Remove a book from the system given its ID.",
    responses={
        200: {"description": "Book deleted successfully."},
        404: {"description": "Book not found."},
    },
)
async def delete_book(book_id: int, session: SessionDep, current_user: CurrentUser, crud_event_queue: SSEQueueDep):
    book = session.get(Books, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    
    await crud_event_queue.put(f"Book deleted: {book.title} by {book.author} (ID: {book_id})")
    
    return book
