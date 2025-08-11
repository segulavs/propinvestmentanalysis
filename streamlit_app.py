import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import json
import os
import time # Added for debounce mechanism
import pickle # For saving/loading results

# Page configuration
st.set_page_config(
    page_title="Return Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f2f6, #ffffff);
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    
    .positive-impact {
        border-left-color: #2ca02c;
    }
    
    .negative-impact {
        border-left-color: #d62728;
    }
    
    .stSlider > div > div > div > div {
        background: #1f77b4;
    }
    
    .stSelectbox > div > div > div > div {
        background: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Supported currencies
SUPPORTED_CURRENCIES = {
    'USD': {'name': 'US Dollar', 'symbol': '$'},
    'EUR': {'name': 'Euro', 'symbol': '€'},
    'GBP': {'name': 'British Pound', 'symbol': '£'},
    'INR': {'name': 'Indian Rupee', 'symbol': '₹'},
    'AED': {'name': 'UAE Dirham', 'symbol': 'د.إ'}
}

# Settings file path
SETTINGS_FILE = 'user_settings.json'

def load_settings():
    """Load user settings from file"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                if isinstance(settings, dict):
                    return settings
    except Exception as e:
        st.error(f"Error loading settings: {str(e)}")
    
    # Return default settings if file doesn't exist or is invalid
    return {
        'investmentCurrency': 'USD',
        'propertyCurrency': 'USD',
        'returnRate': 8.0,
        'payments': []
    }

def save_settings(settings):
    """Save user settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving settings: {str(e)}")
        return False

def fetch_live_exchange_rate(from_currency, to_currency):
    """Fetch live exchange rate from Yahoo Finance"""
    if from_currency == to_currency:
        return 1.0
    
    try:
        # Yahoo Finance API endpoint for currency pairs
        symbol = f"{from_currency}{to_currency}=X"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            if 'meta' in result and 'regularMarketPrice' in result['meta']:
                return result['meta']['regularMarketPrice']
        
        # Fallback: try to get from quotes endpoint
        url_quotes = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        response_quotes = requests.get(url_quotes, headers=headers, timeout=10)
        response_quotes.raise_for_status()
        
        data_quotes = response_quotes.json()
        if 'quoteResponse' in data_quotes and 'result' in data_quotes['quoteResponse']:
            quote = data_quotes['quoteResponse']['result'][0]
            if 'regularMarketPrice' in quote:
                return quote['regularMarketPrice']
        
        return None
        
    except Exception as e:
        st.error(f"Error fetching exchange rate for {from_currency}/{to_currency}: {str(e)}")
        return None

def fetch_historical_exchange_rate(from_currency, to_currency, date):
    """Fetch historical exchange rate from Yahoo Finance for a specific date"""
    if from_currency == to_currency:
        return 1.0
    
    try:
        # Convert date to timestamp for Yahoo Finance API
        target_date = datetime.strptime(date, '%Y-%m-%d')
        
        # Try to get data for a range around the target date
        start_date = target_date - timedelta(days=5)
        end_date = target_date + timedelta(days=5)
        
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())
        
        # Yahoo Finance historical data endpoint
        symbol = f"{from_currency}{to_currency}=X"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_timestamp}&period2={end_timestamp}&interval=1d"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            if 'timestamp' in result and 'indicators' in result and 'quote' in result['indicators']:
                quotes = result['indicators']['quote'][0]
                if 'close' in quotes and quotes['close'] and len(quotes['close']) > 0:
                    timestamps = result['timestamp']
                    close_prices = quotes['close']
                    
                    # Find the closest available date to our target
                    closest_rate = None
                    closest_date_diff = float('inf')
                    
                    for i, timestamp in enumerate(timestamps):
                        if timestamp is not None and close_prices[i] is not None:
                            rate_date = datetime.fromtimestamp(timestamp)
                            date_diff = abs((rate_date - target_date).days)
                            
                            if date_diff < closest_date_diff:
                                closest_date_diff = date_diff
                                closest_rate = close_prices[i]
                    
                    if closest_rate is not None:
                        st.success(f"Found historical rate for {date}: {closest_rate:.4f} (closest available date, diff: {closest_date_diff} days)")
                        return closest_rate
        
        # If still no data, try a wider range
        st.warning(f"Trying wider date range for {date}")
        start_date = target_date - timedelta(days=30)
        end_date = target_date + timedelta(days=30)
        
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_timestamp}&period2={end_timestamp}&interval=1d"
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            if 'timestamp' in result and 'indicators' in result and 'quote' in result['indicators']:
                quotes = result['indicators']['quote'][0]
                if 'close' in quotes and quotes['close'] and len(quotes['close']) > 0:
                    timestamps = result['timestamp']
                    close_prices = quotes['close']
                    
                    # Find the closest available date to our target
                    closest_rate = None
                    closest_date_diff = float('inf')
                    
                    for i, timestamp in enumerate(timestamps):
                        if timestamp is not None and close_prices[i] is not None:
                            rate_date = datetime.fromtimestamp(timestamp)
                            date_diff = abs((rate_date - target_date).days)
                            
                            if date_diff < closest_date_diff:
                                closest_date_diff = date_diff
                                closest_rate = close_prices[i]
                    
                    if closest_rate is not None:
                        st.success(f"Found historical rate for {date}: {closest_rate:.4f} (closest available date, diff: {closest_date_diff} days)")
                        return closest_rate
        
        st.error(f"No historical rate available for {date}, cannot proceed with current rate fallback")
        return None
        
    except Exception as e:
        st.error(f"Error fetching historical exchange rate for {from_currency}/{to_currency} on {date}: {str(e)}")
        return None

def get_exchange_rate(date, from_currency, to_currency):
    """Get exchange rate for a specific date - must be historical rate, not current"""
    if from_currency == to_currency:
        return 1.0
    
    # Get historical rate for the specific date
    historical_rate = fetch_historical_exchange_rate(from_currency, to_currency, date)
    
    if historical_rate is None:
        # If we can't get historical data, we should not proceed with current rate
        raise ValueError(f"Unable to fetch historical exchange rate for {from_currency}/{to_currency} on {date}. Historical data is required for accurate calculations.")
    
    return historical_rate

def get_current_exchange_rate(from_currency, to_currency):
    """Get current exchange rate"""
    if from_currency == to_currency:
        return 1.0
    
    return fetch_live_exchange_rate(from_currency, to_currency) or 1.0

def calculate_returns(payments, desired_return, investment_currency, property_currency):
    """Calculate investment returns with currency conversion and proper ROI calculation"""
    if not payments:
        return None
    
    # Sort payments by date
    payments.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
    
    results = []
    total_invested_investment_currency = 0
    total_invested_property_currency = 0
    total_future_value_property_currency = 0
    total_future_value_investment_currency = 0
    
    # Calculate today's date for ROI calculations
    today = datetime.now()
    
    for payment in payments:
        amount = float(payment['amount'])
        date = payment['date']
        payment_currency = payment.get('amount_currency', investment_currency)
        
        # Convert payment amount to investment currency if different
        if payment_currency != investment_currency:
            try:
                conversion_rate = get_exchange_rate(date, payment_currency, investment_currency)
                amount_in_investment_currency = amount * conversion_rate
            except ValueError as e:
                st.error(f"Payment on {date}: {str(e)}")
                return None
        else:
            amount_in_investment_currency = amount
        
        total_invested_investment_currency += amount_in_investment_currency
        
        # Convert to property currency at investment date
        try:
            if payment_currency == property_currency:
                # If payment is already in property currency, no conversion needed
                amount_in_property_currency = amount
                investment_date_rate = 1.0
            else:
                investment_date_rate = get_exchange_rate(date, investment_currency, property_currency)
                amount_in_property_currency = amount_in_investment_currency * investment_date_rate
        except ValueError as e:
            st.error(f"Payment on {date}: {str(e)}")
            return None
        
        total_invested_property_currency += amount_in_property_currency
        
        # Calculate years from today
        investment_datetime = datetime.strptime(date, '%Y-%m-%d')
        years = (today - investment_datetime).days / 365.25
        
        # Calculate compound interest in property currency
        if years > 0:
            future_value_property_currency = amount_in_property_currency * (1 + desired_return/100) ** years
            interest_earned_property_currency = future_value_property_currency - amount_in_property_currency
        else:
            future_value_property_currency = amount_in_property_currency
            interest_earned_property_currency = 0
        
        total_future_value_property_currency += future_value_property_currency
        
        # Convert back to investment currency at current rate
        current_rate = get_current_exchange_rate(property_currency, investment_currency)
        future_value_investment_currency = future_value_property_currency * current_rate
        total_future_value_investment_currency += future_value_investment_currency
        
        # Calculate pure interest earned (without currency impact)
        if years > 0:
            pure_future_value = amount_in_investment_currency * (1 + desired_return/100) ** years
            pure_interest_earned = pure_future_value - amount_in_investment_currency
        else:
            pure_future_value = amount_in_investment_currency
            pure_interest_earned = 0
        
        # Calculate currency impact
        currency_impact = future_value_investment_currency - pure_future_value
        
        results.append({
            'date': date,
            'amount': amount,
            'amount_currency': payment_currency,
            'amount_in_investment_currency': round(amount_in_investment_currency, 2),
            'amount_in_property_currency': round(amount_in_property_currency, 2),
            'investment_date_rate': round(investment_date_rate, 4),
            'years': round(years, 2),
            'future_value_investment_currency': round(future_value_investment_currency, 2),
            'future_value_property_currency': round(future_value_property_currency, 2),
            'pure_interest_earned_investment_currency': round(pure_interest_earned, 2),
            'pure_interest_earned_property_currency': round(pure_interest_earned * current_rate, 2),
            'currency_impact': round(currency_impact, 2)
        })
    
    # Calculate time-weighted ROI and other metrics
    total_pure_interest = 0
    total_currency_impact = 0
    
    # Calculate weighted average time for investments
    weighted_time = 0
    total_weight = 0
    
    for payment in results:
        amount_inv = payment['amount_in_investment_currency']
        years = payment['years']
        
        # Weight by investment amount
        weighted_time += amount_inv * years
        total_weight += amount_inv
        
        # Accumulate pure interest
        total_pure_interest += payment['pure_interest_earned_investment_currency']
        total_currency_impact += payment['currency_impact']
    
    # Calculate average investment time
    average_investment_time = weighted_time / total_weight if total_weight > 0 else 0
    
    # Calculate ROI based on time-weighted investments
    if total_invested_investment_currency > 0:
        # Simple ROI: (Total Return - Total Invested) / Total Invested
        simple_roi = (total_future_value_investment_currency - total_invested_investment_currency) / total_invested_investment_currency * 100
        
        # Time-weighted ROI: Annualized return considering investment timing
        if average_investment_time > 0:
            time_weighted_roi = ((total_future_value_investment_currency / total_invested_investment_currency) ** (1 / average_investment_time) - 1) * 100
        else:
            time_weighted_roi = 0
        
        # Pure investment ROI (no currency impact)
        pure_roi = (total_pure_interest / total_invested_investment_currency) * 100 if total_invested_investment_currency > 0 else 0
    else:
        simple_roi = 0
        time_weighted_roi = 0
        pure_roi = 0
    
    # Calculate summary metrics
    summary = {
        'total_invested_investment_currency': total_invested_investment_currency,
        'total_invested_property_currency': total_invested_property_currency,
        'total_future_value_investment_currency': total_future_value_investment_currency,
        'total_future_value_property_currency': total_future_value_property_currency,
        'total_pure_interest': total_pure_interest,
        'total_currency_impact': total_currency_impact,
        'multiplying_factor_investment': total_future_value_investment_currency / total_invested_investment_currency if total_invested_investment_currency > 0 else 0,
        'multiplying_factor_property': total_future_value_property_currency / total_invested_property_currency if total_invested_property_currency > 0 else 0,
        'simple_roi': simple_roi,
        'time_weighted_roi': time_weighted_roi,
        'pure_roi': pure_roi,
        'average_investment_time': average_investment_time,
        'overall_return_rate_investment': pure_roi,
        'overall_return_rate_property': pure_roi
    }
    
    return {
        'results': results,
        'summary': summary
    }

def save_results(results, filename):
    """Save investment results to a pickle file"""
    try:
        with open(filename, 'wb') as f:
            pickle.dump(results, f)
        st.success(f"Results saved to {filename}")
    except Exception as e:
        st.error(f"Error saving results to {filename}: {str(e)}")

def load_results(filename):
    """Load investment results from a pickle file"""
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.warning(f"No saved results found at {filename}")
        return None
    except Exception as e:
        st.error(f"Error loading results from {filename}: {str(e)}")
        return None

def list_saved_results():
    """List all saved results files in the current directory"""
    try:
        results_files = []
        for file in os.listdir('.'):
            if file.startswith('investment_results_') and file.endswith('.pkl'):
                # Extract timestamp from filename
                timestamp_str = file.replace('investment_results_', '').replace('.pkl', '')
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    results_files.append({
                        'filename': file,
                        'timestamp': timestamp,
                        'display_name': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    })
                except ValueError:
                    # Skip files with invalid timestamp format
                    continue
        
        # Sort by timestamp (newest first)
        results_files.sort(key=lambda x: x['timestamp'], reverse=True)
        return results_files
    except Exception as e:
        st.error(f"Error listing saved results: {str(e)}")
        return []

def export_results_to_csv(results, filename):
    """Export investment results to CSV format"""
    try:
        # Create DataFrame from results
        df = pd.DataFrame(results['results'])
        
        # Add summary row
        summary_row = pd.DataFrame([{
            'date': 'SUMMARY',
            'amount': results['summary']['total_invested_investment_currency'],
            'amount_currency': 'TOTAL_INVESTED',
            'amount_in_investment_currency': results['summary']['total_invested_investment_currency'],
            'amount_in_property_currency': results['summary']['total_invested_property_currency'],
            'investment_date_rate': 'N/A',
            'years': 'N/A',
            'future_value_investment_currency': results['summary']['total_future_value_investment_currency'],
            'future_value_property_currency': results['summary']['total_future_value_property_currency'],
            'pure_interest_earned_investment_currency': results['summary']['total_pure_interest'],
            'pure_interest_earned_property_currency': results['summary']['total_pure_interest'],
            'currency_impact': results['summary']['total_currency_impact']
        }])
        
        # Combine data and summary
        export_df = pd.concat([df, summary_row], ignore_index=True)
        
        # Export to CSV
        export_df.to_csv(filename, index=False)
        return True
    except Exception as e:
        st.error(f"Error exporting to CSV: {str(e)}")
        return False

def main():
    # Initialize session state variables
    if 'payments' not in st.session_state:
        st.session_state.payments = []
    
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    if 'calculate_clicked' not in st.session_state:
        st.session_state.calculate_clicked = False
    
    # Main header
    st.title("🏠 Return Calculator - Investment Analysis Tool")
    st.markdown("**Calculate compound interest returns with multi-currency support and house payment tracking**")
    
    # Load saved settings
    settings = load_settings()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Currency selection
        investment_currency = st.selectbox(
            "Investment Currency",
            list(SUPPORTED_CURRENCIES.keys()),
            index=list(SUPPORTED_CURRENCIES.keys()).index(settings.get('investmentCurrency', 'USD')),
            help="Currency in which you're making investments"
        )
        
        property_currency = st.selectbox(
            "Property/Investment Currency",
            list(SUPPORTED_CURRENCIES.keys()),
            index=list(SUPPORTED_CURRENCIES.keys()).index(settings.get('propertyCurrency', 'USD')),
            help="Currency in which the investment property is denominated"
        )
        
        # Investment amount currency selection
        investment_amount_currency = st.selectbox(
            "Investment Amount Currency",
            list(SUPPORTED_CURRENCIES.keys()),
            index=list(SUPPORTED_CURRENCIES.keys()).index(settings.get('investmentAmountCurrency', property_currency)),
            help="Currency in which you want to input investment amounts (defaults to property currency)"
        )
        
        # Initial agreed house amount
        initial_house_amount = st.number_input(
            f"Initial Agreed House Amount ({SUPPORTED_CURRENCIES[property_currency]['symbol']})",
            min_value=0.01,
            value=float(settings.get('initialHouseAmount', 1000000.0)),
            step=10000.0,
            format="%.2f",
            help="Total agreed value of the house in property currency"
        )
        
        # Return rate slider
        return_rate = st.slider(
            "Desired Annual Return Rate (%)",
            min_value=0.0,
            max_value=50.0,
            value=float(settings.get('returnRate', 8.0)),
            step=0.1,
            help="Expected annual return rate for your investments",
            key="return_rate_slider"  # Add key for session state tracking
        )
        
        # Auto-calculate when return rate changes
        if 'previous_return_rate' not in st.session_state:
            st.session_state.previous_return_rate = return_rate
        
        # Check if return rate changed and auto-calculate (with debounce)
        if st.session_state.previous_return_rate != return_rate:
            st.session_state.previous_return_rate = return_rate
            if st.session_state.get('payments') and len(st.session_state.payments) > 0:
                # Add a small delay to prevent excessive calculations while sliding
                if 'last_calculation_time' not in st.session_state:
                    st.session_state.last_calculation_time = 0
                
                current_time = time.time()
                if current_time - st.session_state.last_calculation_time > 0.5:  # 500ms debounce
                    st.session_state.auto_calculate = True
                    st.session_state.last_calculation_time = current_time
                    st.info("🔄 Auto-calculating with new rate...")
        
        # Show auto-calculation status
        if st.session_state.get('auto_calculate', False):
            st.success("⚡ Real-time updates enabled")
        
        # Info about auto-calculation
        st.info("💡 **Auto-calculation**: Results update automatically when you adjust the return rate slider!")
        
        # Info about currency selection
        st.info("💱 **Currency Selection**: Choose which currency to input investment amounts in!")
        
        # Reverse Calculation Section (Sidebar)
        st.sidebar.subheader("🔄 Reverse Calculation")
        
        selling_amount = st.sidebar.number_input(
            "Selling Amount (Property Currency)",
            min_value=0.0,
            value=float(st.session_state.get('selling_amount', 0)),
            step=1000.0,
            help="Enter the amount you want to sell the property for"
        )
        
        # Save selling amount to session state
        if selling_amount != st.session_state.get('selling_amount', 0):
            st.session_state.selling_amount = selling_amount
        
        if st.sidebar.button("Save Selling Amount"):
            st.session_state.selling_amount = selling_amount
            st.sidebar.success("Selling amount saved!")
        
        # Calculate potential returns based on selling amount
        if selling_amount > 0 and 'results' in st.session_state and st.session_state.results:
            results = st.session_state.results
            
            # Get total invested in property currency
            total_invested_property = results['summary']['total_invested_property_currency']
            
            # Calculate returns based on selling amount
            if selling_amount >= initial_house_amount:
                property_appreciation = selling_amount - initial_house_amount
                house_value_portion = initial_house_amount
            else:
                property_appreciation = 0
                house_value_portion = selling_amount
            
            your_investment_percentage = min(total_invested_property / initial_house_amount, 1.0)
            your_share_of_house = house_value_portion * your_investment_percentage
            
            your_total_return = your_share_of_house + property_appreciation
            potential_return = your_total_return - total_invested_property
            
            # Calculate ROI metrics based on selling amount
            if total_invested_property > 0:
                # Simple ROI based on selling amount
                selling_roi = (your_total_return / total_invested_property - 1) * 100
                
                # Time-weighted ROI based on selling amount
                average_investment_time = results['summary']['average_investment_time']
                if average_investment_time > 0:
                    selling_time_weighted_roi = ((your_total_return / total_invested_property) ** (1 / average_investment_time) - 1) * 100
                else:
                    selling_time_weighted_roi = 0
                
                # Annualized return rate
                annualized_return = selling_roi / average_investment_time if average_investment_time > 0 else 0
            else:
                selling_roi = 0
                selling_time_weighted_roi = 0
                annualized_return = 0
            
            # Display reverse calculation results
            st.sidebar.success("**Reverse Calculation Results:**")
            st.sidebar.metric(
                "Your Total Return",
                f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{your_total_return:,.2f}",
                f"{selling_roi:.2f}% ROI"
            )
            
            st.sidebar.metric(
                "Time-Weighted ROI",
                f"{selling_time_weighted_roi:.2f}%",
                f"{annualized_return:.2f}% annually"
            )
            
            # Return breakdown
            st.sidebar.info("**Return Breakdown:**")
            st.sidebar.write(f"• **Your Investment**: {SUPPORTED_CURRENCIES[property_currency]['symbol']}{total_invested_property:,.2f}")
            st.sidebar.write(f"• **Your Share of House**: {SUPPORTED_CURRENCIES[property_currency]['symbol']}{your_share_of_house:,.2f}")
            st.sidebar.write(f"• **Property Appreciation**: {SUPPORTED_CURRENCIES[property_currency]['symbol']}{property_appreciation:,.2f}")
            
            # ROI insights
            if selling_roi > 0:
                st.sidebar.success(f"🎯 **Profitable Exit**: {selling_roi:.1f}% total return")
                if selling_time_weighted_roi > 10:
                    st.sidebar.success("🚀 **Excellent Annual Return**: Above 10% annually!")
                elif selling_time_weighted_roi > 5:
                    st.sidebar.success("📈 **Good Annual Return**: Above 5% annually!")
                else:
                    st.sidebar.info("📊 **Moderate Annual Return**: Below 5% annually")
            else:
                st.sidebar.error(f"📉 **Loss**: {selling_roi:.1f}% total return")
            
            # Investment efficiency
            if your_investment_percentage < 1.0:
                st.sidebar.warning(f"⚠️ **Partial Investment**: You've invested {your_investment_percentage*100:.1f}% of house value")
            else:
                st.sidebar.success("✅ **Full Investment**: You've invested 100% of house value")
        
        # Quick Actions
        st.sidebar.subheader("⚡ Quick Actions")
        
        col_q1, col_q2 = st.columns(2)
        
        with col_q1:
            if st.button("🗑️ Clear All Payments"):
                st.session_state.payments = []
                if 'results' in st.session_state:
                    del st.session_state.results
                st.rerun()
        
        with col_q2:
            if st.button("🔄 Quick Reverse Calc"):
                if 'results' in st.session_state and st.session_state.results:
                    results = st.session_state.results
                    total_invested_property = results['summary']['total_invested_property_currency']
                    
                    # Calculate break-even point
                    if total_invested_property > 0:
                        break_even_amount = total_invested_property
                        break_even_percentage = (break_even_amount / initial_house_amount) * 100 if initial_house_amount > 0 else 0
                        
                        st.sidebar.info("**Break-Even Analysis:**")
                        st.sidebar.write(f"• **Break-Even Amount**: {SUPPORTED_CURRENCIES[property_currency]['symbol']}{break_even_amount:,.2f}")
                        st.sidebar.write(f"• **Break-Even %**: {break_even_percentage:.1f}% of house value")
                        
                        # House value comparison
                        if initial_house_amount > 0:
                            st.sidebar.info("**House Value Comparison:**")
                            st.sidebar.write(f"• **Original Price**: {SUPPORTED_CURRENCIES[property_currency]['symbol']}{initial_house_amount:,.2f}")
                            st.sidebar.write(f"• **Your Investment**: {SUPPORTED_CURRENCIES[property_currency]['symbol']}{total_invested_property:,.2f}")
                            st.sidebar.write(f"• **Remaining**: {SUPPORTED_CURRENCIES[property_currency]['symbol']}{initial_house_amount - total_invested_property:,.2f}")
                else:
                    st.sidebar.warning("Calculate returns first!")
        
        # Settings management
        st.sidebar.subheader("💾 Settings")
        
        col_set1, col_set2 = st.columns(2)
        
        with col_set1:
            if st.button("💾 Save Settings"):
                current_settings = {
                    'investmentCurrency': investment_currency,
                    'propertyCurrency': property_currency,
                    'investmentAmountCurrency': investment_amount_currency,
                    'returnRate': return_rate,
                    'payments': st.session_state.get('payments', []),
                    'initialHouseAmount': initial_house_amount,
                    'sellingAmount': st.session_state.get('selling_amount', 0)
                }
                if save_settings(current_settings):
                    st.sidebar.success("Settings saved!")
                else:
                    st.sidebar.error("Failed to save settings")
        
        with col_set2:
            if st.button("📂 Load Settings"):
                loaded_settings = load_settings()
                if loaded_settings:
                    st.session_state['payments'] = loaded_settings.get('payments', [])
                    if 'selling_amount' in loaded_settings:
                        st.session_state['selling_amount'] = loaded_settings.get('selling_amount', 0)
                    st.sidebar.success("Settings loaded!")
                    st.rerun()
                else:
                    st.sidebar.warning("No saved settings found")
        
        # Results management
        st.sidebar.subheader("💾 Results Management")
        
        # Save results
        if 'results' in st.session_state and st.session_state.results:
            col_res1, col_res2, col_res3 = st.columns(3)
            
            with col_res1:
                if st.button("💾 Save Results"):
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"investment_results_{timestamp}.pkl"
                    
                    # Save results
                    save_results(st.session_state.results, filename)
                    
                    # Also save a summary text file
                    summary_filename = f"investment_summary_{timestamp}.txt"
                    try:
                        with open(summary_filename, 'w') as f:
                            f.write("INVESTMENT RESULTS SUMMARY\n")
                            f.write("=" * 50 + "\n\n")
                            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"Investment Currency: {investment_currency}\n")
                            f.write(f"Property Currency: {property_currency}\n")
                            f.write(f"Return Rate: {return_rate}%\n\n")
                            
                            f.write("SUMMARY:\n")
                            f.write(f"Total Invested: {SUPPORTED_CURRENCIES[investment_currency]['symbol']}{st.session_state.results['summary']['total_invested_investment_currency']:,.2f}\n")
                            f.write(f"Future Value: {SUPPORTED_CURRENCIES[investment_currency]['symbol']}{st.session_state.results['summary']['total_future_value_investment_currency']:,.2f}\n")
                            f.write(f"Total ROI: {st.session_state.results['summary']['pure_roi']:.2f}%\n")
                            f.write(f"Total Interest: {SUPPORTED_CURRENCIES[investment_currency]['symbol']}{st.session_state.results['summary']['total_pure_interest']:,.2f}\n\n")
                            
                            f.write("PAYMENTS:\n")
                            for payment in st.session_state.results['results']:
                                f.write(f"- {payment['date']}: {SUPPORTED_CURRENCIES[payment['amount_currency']]['symbol']}{payment['amount']:,.2f}\n")
                        
                        st.sidebar.success(f"Results and summary saved!")
                    except Exception as e:
                        st.sidebar.warning(f"Results saved, but summary file failed: {str(e)}")
            
            with col_res2:
                if st.button("📊 Export CSV"):
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    csv_filename = f"investment_results_{timestamp}.csv"
                    
                    # Export to CSV
                    if export_results_to_csv(st.session_state.results, csv_filename):
                        st.sidebar.success(f"Results exported to {csv_filename}!")
                    else:
                        st.sidebar.error("Failed to export CSV")
            
            with col_res3:
                if st.button("📂 Load Results"):
                    # Show previously saved results
                    saved_files = list_saved_results()
                    
                    if saved_files:
                        st.sidebar.write("**Previously saved results:**")
                        
                        # Create a selectbox for saved files
                        selected_file = st.sidebar.selectbox(
                            "Choose a saved results file:",
                            options=[f['display_name'] for f in saved_files],
                            key="saved_results_selector"
                        )
                        
                        if st.sidebar.button("Load Selected File"):
                            # Find the selected file
                            selected_file_info = next(f for f in saved_files if f['display_name'] == selected_file)
                            
                            # Load the results
                            loaded_results = load_results(selected_file_info['filename'])
                            
                            if loaded_results:
                                st.session_state.results = loaded_results
                                st.sidebar.success(f"Results loaded from {selected_file_info['filename']}!")
                                st.rerun()
                    else:
                        st.sidebar.info("No previously saved results found")
                    
                    # Also allow file upload
                    st.sidebar.write("**Or upload a results file:**")
                    uploaded_file = st.sidebar.file_uploader(
                        "Choose a results file (.pkl)",
                        type=['pkl'],
                        key="results_uploader"
                    )
                    
                    if uploaded_file is not None:
                        try:
                            # Load the uploaded file
                            loaded_results = pickle.load(uploaded_file)
                            
                            # Validate the loaded results structure
                            if isinstance(loaded_results, dict) and 'summary' in loaded_results and 'results' in loaded_results:
                                st.session_state.results = loaded_results
                                st.sidebar.success("Results loaded successfully!")
                                st.rerun()
                            else:
                                st.sidebar.error("Invalid results file format")
                        except Exception as e:
                            st.sidebar.error(f"Error loading results: {str(e)}")
        else:
            st.sidebar.info("Calculate returns first to save/load results")
        
        # File management section
        st.sidebar.subheader("🗂️ File Management")
        
        # Show saved files and allow deletion
        saved_files = list_saved_results()
        if saved_files:
            st.sidebar.write(f"**Found {len(saved_files)} saved results files:**")
            
            # Create a selectbox for file deletion
            file_to_delete = st.sidebar.selectbox(
                "Select file to delete:",
                options=[f['display_name'] for f in saved_files],
                key="delete_file_selector"
            )
            
            if st.sidebar.button("🗑️ Delete Selected File", type="secondary"):
                # Find the selected file
                selected_file_info = next(f for f in saved_files if f['display_name'] == file_to_delete)
                
                try:
                    # Delete the .pkl file
                    os.remove(selected_file_info['filename'])
                    
                    # Also try to delete the corresponding .txt summary file
                    summary_filename = selected_file_info['filename'].replace('.pkl', '.txt')
                    if os.path.exists(summary_filename):
                        os.remove(summary_filename)
                    
                    st.sidebar.success(f"File {selected_file_info['filename']} deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error deleting file: {str(e)}")
        else:
            st.sidebar.info("No saved results files found")
        
        # Live exchange rate display
        if investment_currency != property_currency:
            st.sidebar.subheader("💱 Live Exchange Rate")
            if st.sidebar.button("🔄 Refresh Rate"):
                with st.spinner("Fetching live rate..."):
                    live_rate = get_current_exchange_rate(investment_currency, property_currency)
                    if live_rate:
                        st.sidebar.success(f"**{investment_currency}/{property_currency}**: {live_rate:.4f}")
                    else:
                        st.sidebar.error("Unable to fetch live rate")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    # Auto-calculate if return rate changed
    if st.session_state.get('auto_calculate', False) and st.session_state.get('payments'):
        # Show calculation progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("🔄 Updating calculations..."):
            # Simulate progress for better UX
            for i in range(100):
                progress_bar.progress(i + 1)
                status_text.text(f"Calculating returns at {return_rate}%... ({i+1}%)")
                time.sleep(0.01)  # Small delay for visual effect
            
            results = calculate_returns(
                st.session_state.payments,
                return_rate,
                investment_currency,
                property_currency
            )
            
            if results:
                st.session_state.results = results
                st.session_state.auto_calculate = False  # Reset flag
                progress_bar.progress(100)
                status_text.text("✅ Calculations complete!")
                st.success("✅ Returns updated automatically!")
                time.sleep(1)  # Show success message briefly
                progress_bar.empty()
                status_text.empty()
            else:
                st.error("❌ Failed to update calculations")
                st.session_state.auto_calculate = False
                progress_bar.empty()
                status_text.empty()
    
    with col1:
        st.header("📊 Investment Payments")
        
        # Initialize payments in session state
        if 'payments' not in st.session_state:
            st.session_state.payments = settings.get('payments', [])
        
        # Add new payment
        with st.expander("➕ Add New Payment", expanded=False):
            col_date, col_amount = st.columns(2)
            
            with col_date:
                payment_date = st.date_input("Payment Date", value=datetime.now())
            
            with col_amount:
                payment_amount = st.number_input(
                    f"Amount ({SUPPORTED_CURRENCIES[investment_amount_currency]['symbol']})",
                    min_value=0.01,
                    value=1000.0,
                    step=100.0,
                    format="%.2f"
                )
                
                # Calculate and display percentage of house amount
                if initial_house_amount > 0:
                    # Calculate percentage of house amount
                    if investment_amount_currency == property_currency:
                        # If input currency is already property currency, no conversion needed
                        percentage_of_house = (payment_amount / initial_house_amount) * 100
                        st.info(f"📊 This payment represents **{percentage_of_house:.2f}%** of the house value")
                    else:
                        # Convert payment amount to property currency for percentage calculation
                        try:
                            current_rate = get_current_exchange_rate(investment_amount_currency, property_currency)
                            payment_in_property_currency = payment_amount * current_rate
                            percentage_of_house = (payment_in_property_currency / initial_house_amount) * 100
                            st.info(f"📊 This payment represents **{percentage_of_house:.2f}%** of the house value")
                        except:
                            st.info(f"📊 Enter amount to see percentage of house value")
                else:
                    st.info("📊 Set house amount to see payment percentages")
            
            if st.button("Add Payment"):
                new_payment = {
                    'date': payment_date.strftime('%Y-%m-%d'),
                    'amount': payment_amount,
                    'amount_currency': investment_amount_currency
                }
                st.session_state.payments.append(new_payment)
                
                # Calculate percentage for success message
                if investment_amount_currency == property_currency:
                    # If input currency is already property currency, no conversion needed
                    percentage_of_house = (payment_amount / initial_house_amount) * 100
                    st.success(f"Added payment: {SUPPORTED_CURRENCIES[investment_amount_currency]['symbol']}{payment_amount:,.2f} on {payment_date.strftime('%Y-%m-%d')} ({percentage_of_house:.2f}% of house)")
                else:
                    try:
                        current_rate = get_current_exchange_rate(investment_amount_currency, property_currency)
                        payment_in_property_currency = payment_amount * current_rate
                        percentage_of_house = (payment_in_property_currency / initial_house_amount) * 100
                        st.success(f"Added payment: {SUPPORTED_CURRENCIES[investment_amount_currency]['symbol']}{payment_amount:,.2f} on {payment_date.strftime('%Y-%m-%d')} ({percentage_of_house:.2f}% of house)")
                    except:
                        st.success(f"Added payment: {SUPPORTED_CURRENCIES[investment_amount_currency]['symbol']}{payment_amount:,.2f} on {payment_date.strftime('%Y-%m-%d')}")
                
                st.rerun()
        
        # Create DataFrame for payments with percentage calculations
        if st.session_state.payments:
            payments_data = []
            for payment in st.session_state.payments:
                # Calculate percentage of house amount
                try:
                    current_rate = get_current_exchange_rate(payment['amount_currency'], property_currency)
                    payment_in_property_currency = payment['amount'] * current_rate
                    percentage_of_house = (payment_in_property_currency / initial_house_amount) * 100
                except:
                    percentage_of_house = 0
                
                payments_data.append({
                    'date': payment['date'],
                    'amount': payment['amount'],
                    'amount_currency': payment['amount_currency'],
                    'percentage_of_house': percentage_of_house
                })
            
            payments_df = pd.DataFrame(payments_data)
            payments_df['date'] = pd.to_datetime(payments_df['date'])
            payments_df = payments_df.sort_values('date')
            
            # Format the DataFrame for display
            display_payments_df = payments_df.copy()
            display_payments_df['amount'] = display_payments_df.apply(
                lambda row: f"{SUPPORTED_CURRENCIES[row['amount_currency']]['symbol']}{row['amount']:,.2f}", 
                axis=1
            )
            display_payments_df['percentage_of_house'] = display_payments_df['percentage_of_house'].apply(
                lambda x: f"{x:.2f}%" if x > 0 else "N/A"
            )
            
            # Display payments table
            st.dataframe(
                display_payments_df,
                column_config={
                    "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "amount": st.column_config.TextColumn("Amount"),
                    "amount_currency": st.column_config.TextColumn("Currency"),
                    "percentage_of_house": st.column_config.TextColumn("House %")
                },
                hide_index=True
            )
            
            # Payment summary
            if st.session_state.payments:
                st.subheader("📊 Payment Summary")
                
                # Calculate total percentage covered
                total_percentage_covered = sum(payments_data[i]['percentage_of_house'] for i in range(len(payments_data)))
                remaining_percentage = 100 - total_percentage_covered
                remaining_amount = (remaining_percentage / 100) * initial_house_amount
                
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                
                with col_sum1:
                    st.metric(
                        "Total Payments",
                        f"{len(st.session_state.payments)}",
                        f"Payments made"
                    )
                
                with col_sum2:
                    # Calculate total amount in property currency
                    total_amount_property = 0
                    for payment in st.session_state.payments:
                        if payment['amount_currency'] == property_currency:
                            total_amount_property += payment['amount']
                        else:
                            try:
                                current_rate = get_current_exchange_rate(payment['amount_currency'], property_currency)
                                total_amount_property += payment['amount'] * current_rate
                            except:
                                total_amount_property += payment['amount']  # Fallback
                    
                    st.metric(
                        "House Amount Covered",
                        f"{total_percentage_covered:.2f}%",
                        f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{total_amount_property:,.2f}"
                    )
                
                with col_sum3:
                    st.metric(
                        "Remaining Amount",
                        f"{remaining_percentage:.2f}%",
                        f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{remaining_amount:,.2f}"
                    )
                
                # Progress bar for house payment completion
                progress_value = min(max(total_percentage_covered / 100, 0.0), 1.0)  # Ensure value is between 0 and 1
                st.progress(progress_value, text=f"House Payment Progress: {total_percentage_covered:.1f}% Complete")
                
                if total_percentage_covered >= 100:
                    st.success("🎉 **Congratulations!** You have fully paid for the house!")
                elif total_percentage_covered >= 80:
                    st.info("🏠 **Great progress!** You're almost there!")
                elif total_percentage_covered >= 50:
                    st.info("🏠 **Halfway there!** Keep going!")
                else:
                    st.info("🏠 **Getting started!** Every payment counts!")
            
            # Remove payments
            if st.session_state.payments:
                st.subheader("🗑️ Remove Payments")
                
                col_remove1, col_remove2 = st.columns([3, 1])
                
                with col_remove1:
                    # Create options with percentage information
                    payment_options = []
                    for payment in st.session_state.payments:
                        if payment['amount_currency'] == property_currency:
                            # If payment currency is already property currency, no conversion needed
                            percentage_of_house = (payment['amount'] / initial_house_amount) * 100
                            payment_options.append(f"{payment['date']} - {SUPPORTED_CURRENCIES[payment['amount_currency']]['symbol']}{payment['amount']:,.2f} ({percentage_of_house:.2f}% of house)")
                        else:
                            try:
                                current_rate = get_current_exchange_rate(payment['amount_currency'], property_currency)
                                payment_in_property_currency = payment['amount'] * current_rate
                                percentage_of_house = (payment_in_property_currency / initial_house_amount) * 100
                                payment_options.append(f"{payment['date']} - {SUPPORTED_CURRENCIES[payment['amount_currency']]['symbol']}{payment['amount']:,.2f} ({percentage_of_house:.2f}% of house)")
                            except:
                                payment_options.append(f"{payment['date']} - {SUPPORTED_CURRENCIES[payment['amount_currency']]['symbol']}{payment['amount']:,.2f}")
                    
                    payment_to_remove = st.selectbox(
                        "Select payment to remove:",
                        options=payment_options,
                        index=0
                    )
                
                with col_remove2:
                    if st.button("Remove"):
                        # Find and remove the selected payment
                        for i, payment in enumerate(st.session_state.payments):
                            if payment['amount_currency'] == property_currency:
                                # If payment currency is already property currency, no conversion needed
                                percentage_of_house = (payment['amount'] / initial_house_amount) * 100
                                payment_option = f"{payment['date']} - {SUPPORTED_CURRENCIES[payment['amount_currency']]['symbol']}{payment['amount']:,.2f} ({percentage_of_house:.2f}% of house)"
                            else:
                                try:
                                    current_rate = get_current_exchange_rate(payment['amount_currency'], property_currency)
                                    payment_in_property_currency = payment['amount'] * current_rate
                                    percentage_of_house = (payment_in_property_currency / initial_house_amount) * 100
                                    payment_option = f"{payment['date']} - {SUPPORTED_CURRENCIES[payment['amount_currency']]['symbol']}{payment['amount']:,.2f} ({percentage_of_house:.2f}% of house)"
                                except:
                                    payment_option = f"{payment['date']} - {SUPPORTED_CURRENCIES[payment['amount_currency']]['symbol']}{payment['amount']:,.2f}"
                            
                            if payment_option == payment_to_remove:
                                removed = st.session_state.payments.pop(i)
                                if removed['amount_currency'] == property_currency:
                                    # If payment currency is already property currency, no conversion needed
                                    percentage_of_house = (removed['amount'] / initial_house_amount) * 100
                                    st.success(f"Removed payment: {removed['date']} - {SUPPORTED_CURRENCIES[removed['amount_currency']]['symbol']}{removed['amount']:,.2f} ({percentage_of_house:.2f}% of house)")
                                else:
                                    try:
                                        current_rate = get_current_exchange_rate(removed['amount_currency'], property_currency)
                                        payment_in_property_currency = removed['amount'] * current_rate
                                        percentage_of_house = (payment_in_property_currency / initial_house_amount) * 100
                                        st.success(f"Removed payment: {removed['date']} - {SUPPORTED_CURRENCIES[removed['amount_currency']]['symbol']}{removed['amount']:,.2f} ({percentage_of_house:.2f}% of house)")
                                    except:
                                        st.success(f"Removed payment: {removed['date']} - {SUPPORTED_CURRENCIES[removed['amount_currency']]['symbol']}{removed['amount']:,.2f}")
                                st.rerun()
                                break
        else:
            st.info("No payments added yet. Add your first investment payment above.")
    
    with col2:
        st.header("📈 Quick Actions")
        
        # Quick Actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Calculate Returns", type="primary"):
                if not st.session_state.payments:
                    st.warning("Please add at least one payment first.")
                else:
                    with st.spinner("Calculating returns..."):
                        results = calculate_returns(
                            st.session_state.payments,
                            return_rate,
                            investment_currency,
                            property_currency
                        )
                        
                        if results:
                            st.session_state.results = results
                            st.success("Calculations complete!")
                            st.rerun()
                        else:
                            st.error("Failed to calculate returns. Please check your inputs.")
        
        with col2:
            if st.button("🗑️ Clear All Payments"):
                st.session_state.payments = []
                if 'results' in st.session_state:
                    del st.session_state.results
                st.success("All payments cleared!")
                st.rerun()
        
        with col3:
            if st.button("🔄 Quick Reverse Calc"):
                # Check if we have results first
                if 'results' in st.session_state and st.session_state.results:
                    # Show quick reverse calculation
                    st.info("**Quick Reverse Calculation**")
                    
                    # Calculate total invested
                    total_invested = sum(p['amount_in_property_currency'] for p in st.session_state.results['results'])
                    
                    # Show break-even point
                    st.metric(
                        "Break-Even Point",
                        f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{total_invested:,.2f}",
                        "Recover your investment"
                    )
                    
                    # Show house value comparison
                    if total_invested > initial_house_amount:
                        st.warning(f"🏠 **Above House Value**: You've invested {SUPPORTED_CURRENCIES[property_currency]['symbol']}{total_invested - initial_house_amount:,.2f} more than house value")
                    elif total_invested < initial_house_amount:
                        st.info(f"🏠 **Below House Value**: You need {SUPPORTED_CURRENCIES[property_currency]['symbol']}{initial_house_amount - total_invested:,.2f} more to reach house value")
                    else:
                        st.success("🏠 **At House Value**: Perfect match!")
                    
                    st.info("💡 Use the sidebar for detailed reverse calculation analysis")
                else:
                    st.warning("Please calculate returns first to use reverse calculation")
    
    # Display results if available
    if 'results' in st.session_state and st.session_state.results:
        results = st.session_state.results
        
        st.header("📊 Investment Results")
        
        # Summary metrics in columns
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Invested",
                f"{SUPPORTED_CURRENCIES[investment_currency]['symbol']}{results['summary']['total_invested_investment_currency']:,.2f}",
                f"({SUPPORTED_CURRENCIES[property_currency]['symbol']}{results['summary']['total_invested_property_currency']:,.2f})"
            )
        
        with col2:
            st.metric(
                "Future Value",
                f"{SUPPORTED_CURRENCIES[investment_currency]['symbol']}{results['summary']['total_future_value_investment_currency']:,.2f}",
                f"({SUPPORTED_CURRENCIES[property_currency]['symbol']}{results['summary']['total_future_value_property_currency']:,.2f})"
            )
        
        with col3:
            st.metric(
                "Pure Interest (No FX)",
                f"{SUPPORTED_CURRENCIES[investment_currency]['symbol']}{results['summary']['total_pure_interest']:,.2f}",
                f"{results['summary']['pure_roi']:.2f}% ROI"
            )
        
        with col4:
            # Currency impact metric
            st.metric(
                "Currency Impact",
                f"{SUPPORTED_CURRENCIES[investment_currency]['symbol']}{results['summary']['total_currency_impact']:,.2f}"
            )
            # Show positive/negative impact below
            if results['summary']['total_currency_impact'] > 0:
                st.success("💰 Positive currency impact")
            elif results['summary']['total_currency_impact'] < 0:
                st.error("📉 Negative currency impact")
            else:
                st.info("⚖️ No currency impact")
        
        with col5:
            # Time-weighted ROI metric
            st.metric(
                "Time-Weighted ROI",
                f"{results['summary']['time_weighted_roi']:.2f}%",
                f"{results['summary']['average_investment_time']:.1f} years avg"
            )
        
        # ROI Analysis Section
        st.subheader("📈 ROI Analysis")
        
        col_roi1, col_roi2, col_roi3, col_roi4 = st.columns(4)
        
        with col_roi1:
            st.metric(
                "Simple ROI",
                f"{results['summary']['simple_roi']:.2f}%",
                "Total return on investment"
            )
        
        with col_roi2:
            st.metric(
                "Time-Weighted ROI",
                f"{results['summary']['time_weighted_roi']:.2f}%",
                "Annualized return"
            )
        
        with col_roi3:
            st.metric(
                "Pure Investment ROI",
                f"{results['summary']['pure_roi']:.2f}%",
                "No currency impact"
            )
        
        with col_roi4:
            st.metric(
                "Average Investment Time",
                f"{results['summary']['average_investment_time']:.1f} years",
                "Weighted by amount"
            )
        
        # Reverse Calculation Analysis (Main Content)
        if 'selling_amount' in st.session_state and st.session_state.selling_amount > 0:
            st.subheader("🔄 Reverse Calculation Analysis")
            st.markdown("**ROI Analysis based on your desired selling amount**")
            
            selling_amount = st.session_state.selling_amount
            total_invested_property = results['summary']['total_invested_property_currency']
            
            # Calculate returns based on selling amount
            if selling_amount >= initial_house_amount:
                property_appreciation = selling_amount - initial_house_amount
                house_value_portion = initial_house_amount
            else:
                property_appreciation = 0
                house_value_portion = selling_amount
            
            your_investment_percentage = min(total_invested_property / initial_house_amount, 1.0)
            your_share_of_house = house_value_portion * your_investment_percentage
            your_total_return = your_share_of_house + property_appreciation
            potential_return = your_total_return - total_invested_property
            
            # Calculate ROI metrics based on selling amount
            if total_invested_property > 0:
                selling_roi = (your_total_return / total_invested_property - 1) * 100
                average_investment_time = results['summary']['average_investment_time']
                
                if average_investment_time > 0:
                    selling_time_weighted_roi = ((your_total_return / total_invested_property) ** (1 / average_investment_time) - 1) * 100
                    annualized_return = selling_roi / average_investment_time
                else:
                    selling_time_weighted_roi = 0
                    annualized_return = 0
            else:
                selling_roi = 0
                selling_time_weighted_roi = 0
                annualized_return = 0
            
            # ROI Metrics for Selling Amount
            st.subheader("📊 ROI Metrics (Based on Selling Amount)")
            
            col_sell1, col_sell2, col_sell3, col_sell4 = st.columns(4)
            
            with col_sell1:
                st.metric(
                    "Selling ROI",
                    f"{selling_roi:.2f}%",
                    "Total return on investment"
                )
            
            with col_sell2:
                st.metric(
                    "Annualized ROI",
                    f"{selling_time_weighted_roi:.2f}%",
                    "Yearly return rate"
                )
            
            with col_sell3:
                st.metric(
                    "Your Total Return",
                    f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{your_total_return:,.2f}",
                    f"{selling_roi:.1f}% profit"
                )
            
            with col_sell4:
                st.metric(
                    "Investment Efficiency",
                    f"{your_investment_percentage*100:.1f}%",
                    "Of house value invested"
                )
            
            # Return Breakdown
            st.subheader("💰 Return Breakdown")
            
            col_break1, col_break2, col_break3 = st.columns(3)
            
            with col_break1:
                st.metric(
                    "Your Investment",
                    f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{total_invested_property:,.2f}",
                    f"{your_investment_percentage*100:.1f}% of house"
                )
            
            with col_break2:
                st.metric(
                    "Your Share of House",
                    f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{your_share_of_house:,.2f}",
                    f"Based on {your_investment_percentage*100:.1f}% ownership"
                )
            
            with col_break3:
                st.metric(
                    "Property Appreciation",
                    f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{property_appreciation:,.2f}",
                    f"Full appreciation you keep"
                )
            
            # Reverse Calculation Results Table
            st.subheader("📋 Reverse Calculation Results Table")
            st.write("Detailed breakdown of your reverse calculation analysis:")
            
            # Create reverse calculation data for the table
            reverse_calc_data = [
                {
                    'Metric': 'Initial House Value',
                    'Amount': f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{initial_house_amount:,.2f}",
                    'Currency': property_currency,
                    'Description': 'Original house purchase price'
                },
                {
                    'Metric': 'Your Total Investment',
                    'Amount': f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{total_invested_property:,.2f}",
                    'Currency': property_currency,
                    'Description': f'Your {your_investment_percentage*100:.1f}% share of house value'
                },
                {
                    'Metric': 'Desired Selling Amount',
                    'Amount': f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{selling_amount:,.2f}",
                    'Currency': property_currency,
                    'Description': 'Your target selling price'
                },
                {
                    'Metric': 'Property Appreciation',
                    'Amount': f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{property_appreciation:,.2f}",
                    'Currency': property_currency,
                    'Description': 'Increase in house value since purchase'
                },
                {
                    'Metric': 'Your Share of House Value',
                    'Amount': f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{your_share_of_house:,.2f}",
                    'Currency': property_currency,
                    'Description': f'Your {your_investment_percentage*100:.1f}% of current house value'
                },
                {
                    'Metric': 'Your Total Return',
                    'Amount': f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{your_total_return:,.2f}",
                    'Currency': property_currency,
                    'Description': 'House value share + appreciation'
                },
                {
                    'Metric': 'Pure Profit/Loss',
                    'Amount': f"{SUPPORTED_CURRENCIES[property_currency]['symbol']}{potential_return:,.2f}",
                    'Currency': property_currency,
                    'Description': 'Total return minus your investment'
                },
                {
                    'Metric': 'ROI Percentage',
                    'Amount': f"{selling_roi:.2f}%",
                    'Currency': 'N/A',
                    'Description': 'Return on investment percentage'
                },
                {
                    'Metric': 'Annualized ROI',
                    'Amount': f"{selling_time_weighted_roi:.2f}%",
                    'Currency': 'N/A',
                    'Description': 'Yearly return rate'
                },
                {
                    'Metric': 'Investment Efficiency',
                    'Amount': f"{your_investment_percentage*100:.1f}%",
                    'Currency': 'N/A',
                    'Description': 'Percentage of house value you invested'
                }
            ]
            
            # Display the reverse calculation table
            if reverse_calc_data:
                df_reverse = pd.DataFrame(reverse_calc_data)
                st.dataframe(
                    df_reverse,
                    column_config={
                        "Metric": st.column_config.TextColumn("Calculation Metric", width="medium"),
                        "Amount": st.column_config.TextColumn("Amount/Value", width="medium"),
                        "Currency": st.column_config.TextColumn("Currency", width="small"),
                        "Description": st.column_config.TextColumn("Description", width="large")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            
            # Add scenario analysis below the table
            st.subheader("🎯 Scenario Analysis")
            col_scenario1, col_scenario2 = st.columns(2)
            
            with col_scenario1:
                st.info(f"""
                **📈 Best Case Scenario:**
                - If house sells at **{SUPPORTED_CURRENCIES[property_currency]['symbol']}{selling_amount:,.2f}**
                - Your ROI: **{selling_roi:.2f}%**
                - Annualized return: **{selling_time_weighted_roi:.2f}%**
                - Total profit: **{SUPPORTED_CURRENCIES[property_currency]['symbol']}{potential_return:,.2f}**
                """)
            
            with col_scenario2:
                # Calculate break-even scenario
                break_even_amount = total_invested_property / your_investment_percentage if your_investment_percentage > 0 else 0
                break_even_roi = 0
                
                st.warning(f"""
                **⚖️ Break-Even Scenario:**
                - House must sell for: **{SUPPORTED_CURRENCIES[property_currency]['symbol']}{break_even_amount:,.2f}**
                - At this price, ROI: **{break_even_roi:.2f}%**
                - No profit, no loss
                - Investment efficiency: **{your_investment_percentage*100:.1f}%**
                """)
            
        # Simple results summary
        st.subheader("📊 Results Summary")
        
        col_summary1, col_summary2, col_summary3 = st.columns(3)
        
        with col_summary1:
            st.metric(
                "Total Invested",
                f"{SUPPORTED_CURRENCIES[investment_currency]['symbol']}{results['summary']['total_invested_investment_currency']:,.2f}"
            )
        
        with col_summary2:
            st.metric(
                "Future Value",
                f"{SUPPORTED_CURRENCIES[investment_currency]['symbol']}{results['summary']['total_future_value_investment_currency']:,.2f}"
            )
        
        with col_summary3:
            st.metric(
                "Total ROI",
                f"{results['summary']['pure_roi']:.2f}%",
                f"{SUPPORTED_CURRENCIES[investment_currency]['symbol']}{results['summary']['total_pure_interest']:,.2f}"
            )
        
        # Investment Returns Table
        st.subheader("📋 Investment Returns Breakdown")
        st.write("Detailed breakdown of returns for each individual investment:")
        
        # Create a DataFrame for the investment returns table
        investment_data = []
        for payment in results['results']:
            investment_data.append({
                'Date': payment['date'],
                'Original Amount': f"{SUPPORTED_CURRENCIES[payment['amount_currency']]['symbol']}{payment['amount']:,.2f}",
                'Currency': payment['amount_currency'],
                'Years Invested': f"{payment['years']:.2f}",
                'Future Value': f"{SUPPORTED_CURRENCIES[investment_currency]['symbol']}{payment['future_value_investment_currency']:,.2f}",
                'Interest Earned': f"{SUPPORTED_CURRENCIES[investment_currency]['symbol']}{payment['pure_interest_earned_investment_currency']:,.2f}",
                'ROI %': f"{((payment['future_value_investment_currency'] / payment['amount_in_investment_currency'] - 1) * 100):.2f}%",
                'Exchange Rate': f"{payment['investment_date_rate']:.4f}"
            })
        
        # Display the table
        if investment_data:
            df = pd.DataFrame(investment_data)
            st.dataframe(
                df,
                column_config={
                    "Date": st.column_config.DateColumn("Payment Date", format="YYYY-MM-DD"),
                    "Original Amount": st.column_config.TextColumn("Original Amount"),
                    "Currency": st.column_config.TextColumn("Currency"),
                    "Years Invested": st.column_config.NumberColumn("Years", format="%.2f"),
                    "Future Value": st.column_config.TextColumn("Future Value"),
                    "Interest Earned": st.column_config.TextColumn("Interest Earned"),
                    "ROI %": st.column_config.TextColumn("ROI %"),
                    "Exchange Rate": st.column_config.NumberColumn("Exchange Rate", format="%.4f")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Add summary statistics below the table
            st.subheader("📊 Investment Statistics")
            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
            
            with col_stats1:
                st.metric(
                    "Total Payments",
                    len(results['results']),
                    "Individual investments"
                )
            
            with col_stats2:
                avg_years = sum(payment['years'] for payment in results['results']) / len(results['results'])
                st.metric(
                    "Average Investment Time",
                    f"{avg_years:.1f} years",
                    "Weighted by amount"
                )
            
            with col_stats3:
                max_roi = max(((payment['future_value_investment_currency'] / payment['amount_in_investment_currency'] - 1) * 100) for payment in results['results'])
                st.metric(
                    "Best Single Investment ROI",
                    f"{max_roi:.2f}%",
                    "Highest return on single payment"
                )
            
            with col_stats4:
                min_roi = min(((payment['future_value_investment_currency'] / payment['amount_in_investment_currency'] - 1) * 100) for payment in results['results'])
                st.metric(
                    "Lowest Single Investment ROI",
                    f"{min_roi:.2f}%",
                    "Lowest return on single payment"
                )

if __name__ == "__main__":
    main()
