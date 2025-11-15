from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.finance_manager import Transaction, Budget

router = APIRouter()

class TransactionCreate(BaseModel):
    type: str  # income, expense
    amount: float
    category: str
    description: Optional[str] = None
    date: str  # ISO format

class TransactionResponse(BaseModel):
    id: str
    type: str
    amount: float
    category: str
    description: Optional[str]
    date: str
    created_at: str

    class Config:
        from_attributes = True

class BudgetCreate(BaseModel):
    category: str
    limit_amount: float
    period: str = "monthly"

class BudgetResponse(BaseModel):
    id: str
    category: str
    limit_amount: float
    period: str
    spent: float = 0
    remaining: float = 0
    created_at: str

    class Config:
        from_attributes = True

class CategoryExpense(BaseModel):
    category: str
    amount: float

class FinanceStatsResponse(BaseModel):
    total_income: float
    total_expenses: float
    balance: float
    top_expense_categories: List[CategoryExpense]
    monthly_income: float
    monthly_expenses: float

@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    request: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать транзакцию"""
    
    if request.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type must be income or expense"
        )
    
    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )
    
    transaction = Transaction(
        user_id=current_user.id,
        type=request.type,
        amount=request.amount,
        category=request.category,
        description=request.description,
        date=datetime.fromisoformat(request.date.replace('Z', '+00:00'))
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return TransactionResponse(
        id=transaction.id,
        type=transaction.type,
        amount=transaction.amount,
        category=transaction.category,
        description=transaction.description,
        date=transaction.date.isoformat(),
        created_at=transaction.created_at.isoformat()
    )

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    type: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить транзакции"""
    
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    
    if type:
        query = query.where(Transaction.type == type)
    if category:
        query = query.where(Transaction.category == category)
    
    query = query.order_by(desc(Transaction.date)).limit(limit)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return [
        TransactionResponse(
            id=t.id,
            type=t.type,
            amount=t.amount,
            category=t.category,
            description=t.description,
            date=t.date.isoformat(),
            created_at=t.created_at.isoformat()
        )
        for t in transactions
    ]

@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить транзакцию"""
    
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.user_id == current_user.id
            )
        )
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    await db.delete(transaction)
    await db.commit()

@router.get("/stats", response_model=FinanceStatsResponse)
async def get_finance_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить финансовую статистику"""
    
    # Все транзакции
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == current_user.id)
    )
    all_transactions = result.scalars().all()
    
    # Доходы и расходы
    total_income = sum(t.amount for t in all_transactions if t.type == "income")
    total_expenses = sum(t.amount for t in all_transactions if t.type == "expense")
    balance = total_income - total_expenses
    
    # Топ категорий расходов
    expense_by_category: Dict[str, float] = {}
    for t in all_transactions:
        if t.type == "expense":
            expense_by_category[t.category] = expense_by_category.get(t.category, 0) + t.amount
    
    top_expense_categories = [
        CategoryExpense(category=cat, amount=amount)
        for cat, amount in sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Месячная статистика
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_transactions = [t for t in all_transactions if t.date >= month_start]
    
    monthly_income = sum(t.amount for t in monthly_transactions if t.type == "income")
    monthly_expenses = sum(t.amount for t in monthly_transactions if t.type == "expense")
    
    return FinanceStatsResponse(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        balance=round(balance, 2),
        top_expense_categories=top_expense_categories,
        monthly_income=round(monthly_income, 2),
        monthly_expenses=round(monthly_expenses, 2)
    )

@router.post("/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    request: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать бюджет"""
    
    if request.period not in ["monthly", "weekly", "yearly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period must be monthly, weekly, or yearly"
        )
    
    if request.limit_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit amount must be positive"
        )
    
    budget = Budget(
        user_id=current_user.id,
        category=request.category,
        limit_amount=request.limit_amount,
        period=request.period
    )
    
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    
    return BudgetResponse(
        id=budget.id,
        category=budget.category,
        limit_amount=budget.limit_amount,
        period=budget.period,
        spent=0,
        remaining=budget.limit_amount,
        created_at=budget.created_at.isoformat()
    )

@router.get("/budgets", response_model=List[BudgetResponse])
async def get_budgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить бюджеты"""
    
    result = await db.execute(
        select(Budget).where(Budget.user_id == current_user.id)
    )
    budgets = result.scalars().all()
    
    # Получить транзакции для расчёта потраченного
    transactions_result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.user_id == current_user.id,
                Transaction.type == "expense"
            )
        )
    )
    transactions = transactions_result.scalars().all()
    
    response = []
    for budget in budgets:
        # Вычислить период
        if budget.period == "monthly":
            period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif budget.period == "weekly":
            period_start = datetime.utcnow() - timedelta(days=7)
        else:  # yearly
            period_start = datetime.utcnow().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Сумма трат в категории за период
        spent = sum(
            t.amount for t in transactions
            if t.category == budget.category and t.date >= period_start
        )
        
        response.append(BudgetResponse(
            id=budget.id,
            category=budget.category,
            limit_amount=budget.limit_amount,
            period=budget.period,
            spent=round(spent, 2),
            remaining=round(budget.limit_amount - spent, 2),
            created_at=budget.created_at.isoformat()
        ))
    
    return response

@router.delete("/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить бюджет"""
    
    result = await db.execute(
        select(Budget).where(
            and_(
                Budget.id == budget_id,
                Budget.user_id == current_user.id
            )
        )
    )
    budget = result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    await db.delete(budget)
    await db.commit()

@router.get("/categories")
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список категорий"""
    
    result = await db.execute(
        select(Transaction.category)
        .where(Transaction.user_id == current_user.id)
        .distinct()
    )
    
    categories = [row[0] for row in result.all()]
    
    # Дефолтные категории если нет транзакций
    if not categories:
        categories = [
            "Продукты",
            "Транспорт",
            "Развлечения",
            "Здоровье",
            "Образование",
            "Жильё",
            "Одежда",
            "Другое"
        ]
    
    return {"categories": categories}
