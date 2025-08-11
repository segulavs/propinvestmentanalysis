# 💰 Return Calculator - Streamlit Version

A modern, interactive web application built with Streamlit for calculating compound interest returns on investment payments with multi-currency support and historical exchange rate tracking.

## 🚀 Features

### **Core Functionality**
- **Compound Interest Calculator**: Calculate yearly compound interest on multiple investment payments
- **Multi-Currency Support**: USD, EUR, GBP, INR, and AED with live exchange rates
- **Historical Rate Tracking**: Uses actual exchange rates from payment dates (not current rates)
- **Pure Interest Calculation**: Interest earned independent of currency fluctuations
- **Currency Impact Analysis**: Separate analysis of investment performance vs. currency movements

### **Interactive Interface**
- **Real-time Slider**: Adjust return rates with immediate visual feedback
- **Dynamic Charts**: Interactive Plotly charts for investment timeline and return breakdown
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Session Management**: Automatic saving and loading of user preferences

### **Data Visualization**
- **Investment Timeline**: Line chart showing investment amounts vs. future values over time
- **Return Breakdown**: Pie chart displaying investment, interest, and currency impact
- **Interactive Tables**: Sortable and formatted data tables with proper currency symbols
- **Real-time Updates**: Calculations update automatically as you modify parameters

## 🛠️ Installation

### **Prerequisites**
- Python 3.8 or higher
- pip package manager

### **Setup Steps**

1. **Clone or download the project**
   ```bash
   cd "Return Calculator"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

3. **Run the Streamlit app**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open your browser**
   - The app will automatically open at `http://localhost:8501`
   - Or manually navigate to the URL shown in your terminal

## 📱 How to Use

### **1. Configuration (Sidebar)**
- **Investment Currency**: Select the currency you're investing in
- **Property Currency**: Select the currency of your investment property
- **Return Rate Slider**: Drag to set your desired annual return rate (0% - 50%)
- **Live Exchange Rate**: Click "Refresh Rate" to get current exchange rates

### **2. Adding Investments**
- **Expand "Add New Payment"**: Click to open the payment form
- **Select Date**: Choose the investment date
- **Enter Amount**: Input the investment amount
- **Click "Add Payment"**: Payment is added to your portfolio

### **3. Managing Payments**
- **View All Payments**: See all investments in a sortable table
- **Remove Payments**: Select and remove individual payments
- **Clear All**: Remove all payments at once

### **4. Calculating Returns**
- **Click "Calculate Returns"**: Process all payments with current settings
- **View Results**: See summary metrics, detailed breakdown, and charts
- **Interactive Charts**: Hover over charts for detailed information

### **5. Saving Settings**
- **Auto-save**: Settings are automatically saved as you work
- **Manual Save**: Click "Save Settings" to explicitly save
- **Load Settings**: Restore previously saved configurations

## 📊 Understanding the Results

### **Summary Metrics**
- **Total Invested**: Original investment amounts in both currencies
- **Future Value**: Projected value including compound interest and currency effects
- **Pure Interest**: Investment returns without currency impact
- **Currency Impact**: Additional gains/losses from exchange rate movements

### **Detailed Breakdown Table**
| Column | Description |
|--------|-------------|
| **Payment Date** | When the investment was made |
| **Amount (Investment)** | Original amount in investment currency |
| **Amount (Property)** | Converted amount in property currency |
| **Exchange Rate** | Historical rate on investment date |
| **Years Invested** | Time since investment |
| **Future Value** | Final value in investment currency |
| **Interest Earned** | Pure investment returns (no FX impact) |
| **Currency Impact** | Effect of currency movements |

### **Charts and Visualizations**
- **Investment Timeline**: Shows investment amounts and future values over time
- **Return Breakdown**: Pie chart of investment, interest, and currency impact
- **Interactive Features**: Hover for details, zoom, and pan capabilities

## 🔧 Technical Details

### **Exchange Rate Sources**
- **Live Rates**: Yahoo Finance API for current exchange rates
- **Historical Rates**: Yahoo Finance historical data with date range searching
- **Fallback Handling**: Graceful error handling for unavailable rates

### **Calculation Methodology**
- **Compound Interest**: `Future Value = Principal × (1 + Rate)^Years`
- **Currency Conversion**: Historical rates at investment date, current rates for future value
- **Pure Returns**: Interest calculated without currency impact
- **FX Impact**: Difference between actual returns and pure investment returns

### **Data Persistence**
- **Settings File**: `user_settings.json` stores user preferences
- **Session State**: Streamlit session state for temporary data
- **Auto-save**: Automatic saving of user configurations

## 🌟 Key Advantages Over Flask Version

### **User Experience**
- **Real-time Updates**: Instant feedback as you adjust parameters
- **Interactive Charts**: Rich visualizations with Plotly
- **Responsive Design**: Better mobile and tablet experience
- **Modern UI**: Clean, professional appearance with Streamlit components

### **Functionality**
- **Session Management**: Better state handling and persistence
- **Data Tables**: Interactive, sortable dataframes
- **Visual Analytics**: Charts and graphs for better insights
- **Streamlined Workflow**: More intuitive user interface

### **Development**
- **Easier Maintenance**: Single Python file vs. HTML/CSS/JS
- **Better Error Handling**: Streamlit's built-in error display
- **Responsive Layouts**: Automatic responsive design
- **Rich Components**: Built-in widgets and data display

## 🚨 Troubleshooting

### **Common Issues**

1. **Port Already in Use**
   ```bash
   # Kill existing Streamlit processes
   pkill -f streamlit
   # Or use a different port
   streamlit run streamlit_app.py --server.port 8502
   ```

2. **Exchange Rate Errors**
   - Check internet connection
   - Yahoo Finance API may have rate limits
   - Try refreshing rates after a few minutes

3. **Settings Not Saving**
   - Ensure write permissions in the project directory
   - Check if `user_settings.json` is being created
   - Verify Python has file write access

4. **Charts Not Displaying**
   - Ensure Plotly is properly installed
   - Check browser console for JavaScript errors
   - Try refreshing the page

### **Performance Tips**
- **Limit Payments**: Very large numbers of payments may slow calculations
- **Close Unused Tabs**: Multiple browser tabs can impact performance
- **Regular Refreshes**: Refresh the app if it becomes unresponsive

## 🔮 Future Enhancements

### **Planned Features**
- **Export Functionality**: PDF reports and Excel exports
- **Advanced Analytics**: Risk analysis and portfolio optimization
- **Multiple Scenarios**: Compare different investment strategies
- **Real-time Data**: Live market data integration
- **Mobile App**: Native mobile application

### **Customization Options**
- **Theme Selection**: Light/dark mode and color schemes
- **Chart Customization**: User-defined chart types and colors
- **Report Templates**: Customizable report formats
- **API Integration**: Connect to external financial data sources

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📞 Support

For support or questions:
- Check the troubleshooting section above
- Review the code comments for implementation details
- Open an issue on the project repository

---

**Built with ❤️ using Streamlit, Python, and Plotly**

*Transform your investment analysis with modern, interactive tools!*
