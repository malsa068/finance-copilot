"""
Finance Functions for Portfolio Analysis
Provides three core functions for analyzing stock portfolios:
1. get_total_unrealized_gain_loss() - Calculate gains/losses
2. get_daily_change() - Calculate daily portfolio value changes
3. get_portfolio_weights() - Calculate portfolio composition

Uses yfinance API for real-time stock prices.
"""

import yfinance as yf
from typing import List, Dict


def get_total_unrealized_gain_loss(portfolio: List[Dict]) -> Dict:
    """
    Calculate the total unrealized gain/loss for the entire portfolio.
    
    Args:
        portfolio: List of dictionaries with keys:
            - 'ticker': Stock symbol (e.g., 'AAPL')
            - 'shares': Number of shares owned
            - 'purchase_price': Price per share at purchase
    
    Returns:
        Dictionary containing:
            - 'total_gain_loss': Total unrealized gain/loss in dollars
            - 'total_cost_basis': Total amount invested
            - 'total_current_value': Current total portfolio value
            - 'percentage_return': Percentage return on investment
            - 'details': List of per-stock details
    """
    total_cost_basis = 0
    total_current_value = 0
    details = []
    
    for holding in portfolio:
        ticker = holding['ticker']
        shares = holding['shares']
        purchase_price = holding['purchase_price']
        
        try:
            # Get current stock price using yfinance
            stock = yf.Ticker(ticker)
            current_price = stock.info.get('currentPrice') or stock.info.get('regularMarketPrice')
            
            if current_price is None:
                # Fallback: try getting latest price from history
                hist = stock.history(period='1d')
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                else:
                    print(f"Warning: Could not fetch price for {ticker}")
                    continue
            
            # Calculate values
            cost_basis = shares * purchase_price
            current_value = shares * current_price
            gain_loss = current_value - cost_basis
            gain_loss_percentage = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
            
            total_cost_basis += cost_basis
            total_current_value += current_value
            
            details.append({
                'ticker': ticker,
                'shares': shares,
                'purchase_price': purchase_price,
                'current_price': current_price,
                'cost_basis': cost_basis,
                'current_value': current_value,
                'gain_loss': gain_loss,
                'gain_loss_percentage': gain_loss_percentage
            })
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            continue
    
    total_gain_loss = total_current_value - total_cost_basis
    percentage_return = (total_gain_loss / total_cost_basis) * 100 if total_cost_basis > 0 else 0
    
    return {
        'total_gain_loss': total_gain_loss,
        'total_cost_basis': total_cost_basis,
        'total_current_value': total_current_value,
        'percentage_return': percentage_return,
        'details': details
    }


def get_daily_change(portfolio: List[Dict]) -> Dict:
    """
    Calculate the daily change in portfolio value (since yesterday).
    
    Args:
        portfolio: List of dictionaries with keys:
            - 'ticker': Stock symbol (e.g., 'AAPL')
            - 'shares': Number of shares owned
    
    Returns:
        Dictionary containing:
            - 'daily_change_value': Dollar change since yesterday
            - 'daily_change_percentage': Percentage change since yesterday
            - 'current_value': Current total portfolio value
            - 'yesterday_value': Yesterday's portfolio value
            - 'details': List of per-stock daily changes
    """
    current_value = 0
    yesterday_value = 0
    details = []
    
    for holding in portfolio:
        ticker = holding['ticker']
        shares = holding['shares']
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get 2 days of history to compare today vs yesterday
            hist = stock.history(period='2d')
            
            if len(hist) < 2:
                print(f"Warning: Not enough historical data for {ticker}")
                continue
            
            current_price = hist['Close'].iloc[-1]
            yesterday_price = hist['Close'].iloc[-2]
            
            stock_current_value = shares * current_price
            stock_yesterday_value = shares * yesterday_price
            stock_daily_change = stock_current_value - stock_yesterday_value
            stock_daily_change_pct = (stock_daily_change / stock_yesterday_value) * 100 if stock_yesterday_value > 0 else 0
            
            current_value += stock_current_value
            yesterday_value += stock_yesterday_value
            
            details.append({
                'ticker': ticker,
                'shares': shares,
                'current_price': current_price,
                'yesterday_price': yesterday_price,
                'daily_change_value': stock_daily_change,
                'daily_change_percentage': stock_daily_change_pct
            })
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            continue
    
    daily_change_value = current_value - yesterday_value
    daily_change_percentage = (daily_change_value / yesterday_value) * 100 if yesterday_value > 0 else 0
    
    return {
        'daily_change_value': daily_change_value,
        'daily_change_percentage': daily_change_percentage,
        'current_value': current_value,
        'yesterday_value': yesterday_value,
        'details': details
    }


def get_portfolio_weights(portfolio: List[Dict]) -> Dict:
    """
    Calculate the portfolio weight for each stock.
    
    Args:
        portfolio: List of dictionaries with keys:
            - 'ticker': Stock symbol (e.g., 'AAPL')
            - 'shares': Number of shares owned
    
    Returns:
        Dictionary containing:
            - 'total_portfolio_value': Total current portfolio value
            - 'weights': List of dictionaries with ticker and weight percentage
    """
    holdings_values = []
    total_value = 0
    
    for holding in portfolio:
        ticker = holding['ticker']
        shares = holding['shares']
        
        try:
            # Get current stock price using yfinance
            stock = yf.Ticker(ticker)
            current_price = stock.info.get('currentPrice') or stock.info.get('regularMarketPrice')
            
            if current_price is None:
                # Fallback: try getting latest price from history
                hist = stock.history(period='1d')
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                else:
                    print(f"Warning: Could not fetch price for {ticker}")
                    continue
            
            holding_value = shares * current_price
            total_value += holding_value
            
            holdings_values.append({
                'ticker': ticker,
                'shares': shares,
                'current_price': current_price,
                'value': holding_value
            })
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            continue
    
    # Calculate weights
    weights = []
    for holding in holdings_values:
        weight_percentage = (holding['value'] / total_value) * 100 if total_value > 0 else 0
        weights.append({
            'ticker': holding['ticker'],
            'shares': holding['shares'],
            'current_price': holding['current_price'],
            'value': holding['value'],
            'weight_percentage': weight_percentage
        })
    
    # Sort by weight (highest to lowest)
    weights.sort(key=lambda x: x['weight_percentage'], reverse=True)
    
    return {
        'total_portfolio_value': total_value,
        'weights': weights
    }
