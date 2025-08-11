# Live Multi-Currency Return Calculator - Historical Rate Tracking & Settings Persistence

A sophisticated web application built with Python Flask that calculates compound interest returns on investment payments with **live multi-currency support**, **historical exchange rate tracking**, **individual payment conversion analysis**, and **automatic settings persistence** from Yahoo Finance.

## 🌍 **Live Multi-Currency Features**

- **Live Exchange Rates**: Real-time currency conversion using Yahoo Finance API
- **Historical Rate Tracking**: Individual payment date exchange rates for accurate historical analysis
- **Investment Currency Selection**: Choose the currency you're investing in (USD, EUR, GBP, INR, **AED**)
- **Property Currency Selection**: Choose the currency your investment property generates returns in
- **Real-time Rate Updates**: Live exchange rate display with manual refresh capability
- **Currency Impact Analysis**: See how currency fluctuations affect your total returns
- **Dual Currency Display**: View results in both investment and property currencies

## 🆕 **New: Individual Payment Conversion & Historical Tracking**

### **Individual Payment Conversion**
- **Convert Button**: Each payment now has a "Convert" button for instant currency conversion
- **Date-Specific Rates**: Uses historical exchange rates for the exact investment date
- **Real-time Results**: Shows conversion results immediately below each payment
- **Visual Feedback**: Loading states and success/error indicators

### **Historical Rate Analysis**
- **Investment Date Rate**: Exchange rate when the payment was made
- **Current Rate**: Current exchange rate for comparison
- **Rate Change**: Absolute and percentage change in exchange rates over time
- **Color Coding**: Green for positive rate changes, red for negative changes

### **Enhanced Results Table**
- **Historical Rate Column**: Shows the exchange rate on the investment date
- **Current Rate Column**: Shows the current exchange rate
- **Rate Change Column**: Displays both absolute change and percentage change
- **Comprehensive Analysis**: Complete picture of currency movements over time

## 🆕 **New: Settings Persistence & Auto-Save**

### **Automatic Settings Management**
- **Auto-Save**: Automatically saves settings after 2 seconds of inactivity
- **Settings Status**: Real-time display of save status (Saved/Unsaved/Auto-saving)
- **Persistent Storage**: All settings saved to local file (`user_settings.json`)
- **Session Recovery**: Automatically loads previous settings on application restart

### **Manual Settings Control**
- **Save Settings**: Manual save button for immediate settings persistence
- **Load Settings**: Restore previously saved settings at any time
- **Settings Validation**: Ensures all required fields are present before saving
- **Error Handling**: Graceful fallback if settings file is corrupted

### **Persisted Settings Include**
- **Currency Selections**: Investment and property currency preferences
- **Return Rate**: Desired annual return rate percentage
- **Payment Entries**: Complete payment history with dates and amounts
- **User Preferences**: All form inputs and selections

## 🆕 **New: AED (UAE Dirham) Support**

The application now supports **AED (UAE Dirham)** as a fully integrated currency option:
- Investment currency selection
- Property currency selection  
- Live exchange rate fetching
- Historical rate tracking
- Proper currency symbol display (د.إ)
- Complete calculation support

## 📡 **Live Exchange Rate Integration**

### **Yahoo Finance API**
- **Real-time Data**: Fetches current exchange rates from Yahoo Finance
- **Historical Data**: Retrieves exchange rates for specific dates
- **Multiple Endpoints**: Uses both chart and quote APIs for reliability
- **Automatic Fallbacks**: Graceful error handling with fallback mechanisms
- **Rate Refresh**: Manual refresh button for updated rates

### **Historical Rate Fetching**
- **Date-Specific Queries**: Fetches rates for exact investment dates
- **Timestamp Conversion**: Converts dates to Yahoo Finance API format
- **Close Price Data**: Uses daily closing exchange rates for accuracy
- **Fallback Strategy**: Falls back to current rates if historical data unavailable

### **Supported Currency Pairs**
All major currency combinations including:
- USD ↔ EUR, GBP, INR, AED
- EUR ↔ USD, GBP, INR, AED  
- GBP ↔ USD, EUR, INR, AED
- INR ↔ USD, EUR, GBP, AED
- AED ↔ USD, EUR, GBP, INR

## 🎯 **Core Features**

- **Multiple Payment Entries**: Add multiple payments with different dates and amounts
- **Individual Conversion**: Convert each payment individually with date-specific rates
- **Historical Tracking**: Track exchange rate changes for each payment over time
- **Flexible Return Rate**: Set your desired annual return rate (as a percentage)
- **Compound Interest Calculation**: Automatically calculates compound interest for each payment based on time invested
- **Real-time Results**: Instant calculation and display of results
- **Responsive Design**: Modern, mobile-friendly interface
- **Detailed Breakdown**: View individual payment results and summary statistics
- **Settings Persistence**: Automatic and manual save/load of all preferences

## 💱 **How Enhanced Currency Conversion Works**

The application now provides comprehensive historical analysis:

1. **Individual Payment Conversion**: Each payment can be converted individually using historical rates
2. **Historical Rate Fetching**: Retrieves exchange rates for specific investment dates
3. **Rate Change Tracking**: Compares investment date rates with current rates
4. **Investment Conversion**: Converts your investment amount to the property currency using historical rates
5. **Interest Calculation**: Applies compound interest in the property currency over time
6. **Final Conversion**: Converts the future value back to your investment currency using current live rates
7. **Impact Analysis**: Shows the difference between currency-adjusted returns and theoretical returns

### **Enhanced Formula Breakdown:**
```
Step 1: Historical Rate Fetch = Yahoo Finance Historical API Call (Investment Date)
Step 2: Individual Payment Conversion = Amount × Historical Exchange Rate
Step 3: Investment Amount (Property Currency) = Investment Amount × Historical Rate
Step 4: Future Value (Property Currency) = Investment Amount (Property) × (1 + Rate)^Time
Step 5: Current Rate Fetch = Yahoo Finance Live API Call
Step 6: Future Value (Investment Currency) = Future Value (Property) × Current Live Rate
Step 7: Rate Change Analysis = Current Rate - Historical Rate
Step 8: Currency Impact = Actual Returns - Theoretical Returns (No Currency Change)
```

## 📊 **Example Scenarios with Historical Tracking**

### **Scenario 1: USD to AED Investment with Historical Rates**
- Invest $10,000 USD on January 15, 2023
- Property generates returns in AED
- **Historical Rate (Jan 15, 2023)**: 1 USD = 3.6725 AED
- **Current Rate (Today)**: 1 USD = 3.6730 AED
- **Rate Change**: +0.0005 (+0.01%)
- **Result**: Historical conversion + rate change analysis

### **Scenario 2: EUR to GBP Investment with Date-Specific Conversion**
- Invest €8,000 EUR on March 10, 2022
- Property generates returns in GBP
- **Historical Rate (Mar 10, 2022)**: 1 EUR = 0.8345 GBP
- **Current Rate (Today)**: 1 EUR = 0.8567 GBP
- **Rate Change**: +0.0222 (+2.66%)
- **Result**: Significant EUR appreciation vs GBP over time

## 🚀 **Installation & Setup**

### **Prerequisites**
- Python 3.7 or higher
- pip (Python package installer)
- Internet connection for live and historical exchange rate fetching

### **Steps**

1. **Clone or download** the project files to your local machine

2. **Navigate** to the project directory:
   ```bash
   cd "Return Calculator"
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

## 📖 **Enhanced Usage Guide**

1. **Settings Management**:
   - **Auto-Save**: Settings automatically save after 2 seconds of inactivity
   - **Manual Save**: Click "Save Settings" button for immediate persistence
   - **Load Settings**: Click "Load Settings" to restore previous configuration
   - **Status Monitor**: Watch the settings status bar for save state

2. **Select Currencies**:
   - **Investment Currency**: The currency you're investing in (now including AED)
   - **Property Currency**: The currency your investment generates returns in

3. **View Live Exchange Rate**: 
   - Real-time rate display updates automatically
   - Manual refresh button for latest rates
   - Rate shown as "1 [Investment] = X [Property]"

4. **Add Payments**: Click "Add Payment" to add investment entries
   - Set the payment date
   - Enter the payment amount in your investment currency
   - **NEW**: Use "Convert" button for individual payment conversion

5. **Individual Payment Conversion**:
   - Click "Convert" button on any payment
   - See historical exchange rate for that specific date
   - View converted amount in property currency
   - Compare with current rates

6. **Set Return Rate**: Enter your desired annual return rate (e.g., 8.0 for 8%)

7. **Calculate**: Click "Calculate Returns" to see comprehensive results

8. **View Enhanced Results**: 
   - **Summary Cards**: Total invested, future value, total interest, and currency impact
   - **Exchange Rate Analysis**: Detailed currency conversion information with historical tracking
   - **Enhanced Table**: Breakdown of each payment with historical rates, current rates, and rate changes

## 🔄 **Enhanced Exchange Rate Features**

### **Real-time Updates**
- **Automatic Fetching**: Rates update when currencies change
- **Manual Refresh**: Click refresh button for latest rates
- **Error Handling**: Graceful fallback if API is unavailable
- **Loading States**: Visual feedback during rate fetching

### **Historical Rate Tracking**
- **Date-Specific Queries**: Fetches rates for exact investment dates
- **Rate Change Analysis**: Shows how rates moved over time
- **Percentage Changes**: Displays both absolute and percentage rate changes
- **Visual Indicators**: Color-coded rate changes for easy analysis

### **API Reliability**
- **Multiple Endpoints**: Uses both chart and quote APIs
- **Historical Endpoints**: Dedicated historical data API calls
- **Timeout Handling**: 10-second timeout for API calls
- **User-Agent Headers**: Proper browser identification for API access
- **Fallback Mechanisms**: Graceful degradation if primary API fails

## 💾 **Settings Persistence Features**

### **Automatic Management**
- **Auto-Save Timer**: 2-second delay after last change
- **Status Indicators**: Real-time save status display
- **Background Saving**: Non-blocking save operations
- **Error Recovery**: Graceful handling of save failures

### **Manual Control**
- **Save Button**: Immediate settings persistence
- **Load Button**: Restore previous configuration
- **Validation**: Ensures data integrity before saving
- **User Feedback**: Toast notifications for all operations

### **Data Persistence**
- **Local Storage**: Settings saved to `user_settings.json`
- **Session Recovery**: Automatic loading on application restart
- **Data Validation**: Ensures saved data structure integrity
- **Backup Safety**: Graceful fallback to defaults if file corrupted

## 🎨 **Technical Details**

- **Backend**: Python Flask with live and historical Yahoo Finance API integration
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla) with responsive design
- **Styling**: Modern CSS with gradients, shadows, and responsive design
- **Icons**: Font Awesome for UI elements
- **Currency Support**: Multi-currency calculations with historical rate tracking
- **API Integration**: Yahoo Finance for real-time and historical exchange rates
- **Historical Data**: Date-specific exchange rate retrieval and analysis
- **Settings Management**: JSON-based persistence with auto-save functionality

## 📁 **File Structure**

```
Return Calculator/
├── app.py              # Enhanced Flask application with historical API integration
├── requirements.txt    # Python dependencies including requests
├── README.md          # This comprehensive guide
├── user_settings.json # User settings persistence file (auto-generated)
└── templates/
    └── index.html     # Enhanced HTML template with historical tracking features
```

## 🔧 **Customization Options**

You can easily modify the application by:
- Adding more currencies to the `SUPPORTED_CURRENCIES` dictionary
- Integrating alternative exchange rate APIs (Fixer, CurrencyLayer, etc.)
- Modifying the compound interest formula for different scenarios
- Adding new calculation features like inflation adjustment
- Customizing the UI styling and layout
- Implementing rate caching for better performance
- Adding more historical data analysis features
- Extending settings persistence with additional user preferences

## 🚨 **Troubleshooting**

- **Port already in use**: Change the port in `app.py` by modifying `app.run(debug=True, port=5001)`
- **Dependencies not found**: Ensure you're using the correct Python environment and have run `pip install -r requirements.txt`
- **Calculation errors**: Check that all payment amounts are positive numbers and dates are valid
- **Currency conversion issues**: Verify that both currencies are supported
- **API rate limits**: Yahoo Finance may have rate limits; use refresh button sparingly
- **Network issues**: Ensure internet connection for live and historical rate fetching
- **Historical data unavailable**: Some dates may not have historical data; app falls back to current rates
- **Settings save issues**: Check file permissions in the application directory
- **Settings load failures**: Verify `user_settings.json` file integrity

## 🔮 **Future Enhancements**

Potential improvements for the application:
- **Rate Caching**: Store rates locally to reduce API calls
- **Historical Charts**: Visual representation of rate movements over time
- **Multiple API Sources**: Fallback to alternative exchange rate services
- **Rate Alerts**: Notifications for significant rate changes
- **Export Functionality**: PDF/Excel reports with historical rate data
- **Mobile App**: Native mobile application with push notifications
- **Advanced Analytics**: Statistical analysis of rate movements and volatility
- **Cloud Sync**: Synchronize settings across multiple devices
- **User Accounts**: Multi-user support with individual settings
- **Settings Templates**: Pre-configured settings for common scenarios

## 📄 **License**

This project is open source and available under the MIT License.

---

**Happy Historical Multi-Currency Investing with Persistent Settings!** 💰🌍📈📅💾
