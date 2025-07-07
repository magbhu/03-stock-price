import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# Configure the layout
st.set_page_config(page_title="Multi-Bank vs NIFTYBANK Chart", layout="wide")
st.title("📈 Multi-Bank & NIFTYBANK Closing Price Dashboard")

# Upload main bank data
default_bank_file = Path("All_Banks_Combined.csv")
default_nifty_file = Path("niftybank.csv")

bank_file = default_bank_file.open("rb") if default_bank_file.exists() else st.file_uploader("📂 Upload Multi-Bank CSV", type=["csv"])
nifty_file = default_nifty_file.open("rb") if default_nifty_file.exists() else st.file_uploader("📂 Upload NIFTYBANK CSV", type=["csv"])

# Sidebar color picker for NIFTYBANK
nifty_color = st.sidebar.color_picker("🎨 Choose NIFTYBANK Line Color", value="#FFA500")  # Default orange

# Proceed if both files are uploaded
if bank_file and nifty_file:
    try:
        # Load and validate data
        bank_df = pd.read_csv(bank_file)
        nifty_df = pd.read_csv(nifty_file)

        if not {'Bank', 'Date', 'Close'}.issubset(bank_df.columns):
            st.error("Multi-Bank file must contain 'Bank', 'Date', and 'Close' columns.")
        elif not {'Date', 'Close'}.issubset(nifty_df.columns):
            st.error("NIFTYBANK file must contain 'Date' and 'Close' columns.")
        else:
            # Convert date columns
            bank_df['Date'] = pd.to_datetime(bank_df['Date'])
            nifty_df['Date'] = pd.to_datetime(nifty_df['Date'])

            # Sidebar filter: select banks
            bank_list = sorted(bank_df['Bank'].unique())
            selected_banks = st.sidebar.multiselect("🏦 Select Banks", options=bank_list, default=bank_list[:5])

            # Filter bank data
            filtered_df = bank_df[bank_df['Bank'].isin(selected_banks)]

            if not filtered_df.empty and not nifty_df.empty:
                # Create plot
                fig = go.Figure()

                # Plot each bank (left Y-axis, reversed)
                for bank in selected_banks:
                    data = filtered_df[filtered_df['Bank'] == bank]
                    fig.add_trace(go.Scatter(
                        x=data['Date'],
                        y=data['Close'],
                        mode='lines',
                        name=bank,
                        yaxis='y1'
                    ))

                # Plot NIFTYBANK (right Y-axis)
                fig.add_trace(go.Scatter(
                    x=nifty_df['Date'],
                    y=nifty_df['Close'],
                    mode='lines',
                    name='NIFTYBANK',
                    line=dict(color=nifty_color, width=3, dash='dashdot'),
                    yaxis='y2'
                ))

                # Update layout with dual Y-axes
                fig.update_layout(
                    title="📊 Bank Stocks vs NIFTYBANK - Dual Axis View",
                    xaxis=dict(title="Date"),
                    yaxis=dict(title="Bank Closing Price", autorange="reversed"),
                    yaxis2=dict(title="NIFTYBANK Closing Price", overlaying='y', side='right'),
                    legend_title="Symbols",
                    template="plotly_white",
                    height=650
                )

                # Show plot
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Empty data for selected banks or NIFTYBANK.")
    except Exception as e:
        st.error(f"⚠️ Error processing files: {e}")
else:
    st.info("👆 Please upload both CSV files above to begin.")
