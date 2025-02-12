import streamlit as st
import os
from fpdf import FPDF
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Initialize LLM
llm = ChatGroq(
    temperature=0,
    groq_api_key="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",  # Replace with your API key
    model_name="llama-3.3-70b-versatile"
)

# Define the itinerary prompt
itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful travel assistant. Create a {duration}-day itinerary for {city} based on the user's interests: {interests}. For each day, provide a structured plan with timings. Use bullet points and keep it concise."),
    ("human", "Create an itinerary for my trip to {city}.")
])

# Function to estimate budget
def estimate_budget(city: str, duration: int, budget_type: str):
    budget_ranges = {
        "budget": {"accommodation": 1000, "food": 500, "transport": 300, "activities": 700},
        "mid-range": {"accommodation": 4000, "food": 1500, "transport": 1000, "activities": 3000},
        "luxury": {"accommodation": 10000, "food": 5000, "transport": 5000, "activities": 8000}
    }
    if budget_type.lower() not in budget_ranges:
        return {"error": "Invalid budget type"}
    
    breakdown = {key: value * duration for key, value in budget_ranges[budget_type.lower()].items()}
    total_cost = sum(breakdown.values())
    
    return {"breakdown": breakdown, "total_cost": total_cost, "currency": "INR"}

# Function to get recommendations
def get_recommendations(city: str):
    recommendations_data = {
        "Delhi": {
            "attractions": ["Red Fort", "Qutub Minar", "India Gate", "Lotus Temple"],
            "restaurants": ["Indian Accent", "Bukhara", "Saravana Bhavan", "Karim's"]
        },
        "Mumbai": {
            "attractions": ["Gateway of India", "Marine Drive", "Elephanta Caves"],
            "restaurants": ["Leopold Cafe", "BadeMiya", "Trishna"]
        }
    }
    recs = recommendations_data.get(city.title(), None)
    if recs:
        return f"Attractions: {', '.join(recs['attractions'])}\nRestaurants: {', '.join(recs['restaurants'])}"
    return "No specific recommendations available. Please explore local attractions and dining options."

# Function to generate itinerary
def generate_itinerary(city, interests, duration):
    response = llm.invoke(itinerary_prompt.format(city=city, interests=interests, duration=duration))
    return response.content if hasattr(response, "content") else str(response)

# Function to generate PDF
def generate_pdf(itinerary: str, recommendations: str, filename: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Travel Itinerary", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, itinerary)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Attraction & Restaurant Recommendations", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, recommendations)
    pdf.output(filename)

# Streamlit UI
st.title("Travel Itinerary Planner")

city = st.text_input("Enter the city you want to visit:")
interests = st.text_area("Enter your interests (comma-separated):")
duration = st.number_input("Enter the duration of your trip (in days):", min_value=1, step=1)
budget_type = st.selectbox("Select your budget type:", ["budget", "mid-range", "luxury"])

if st.button("Generate Itinerary"):
    if city and interests and duration:
        itinerary = generate_itinerary(city, interests.split(","), duration)
        recommendations = get_recommendations(city)
        budget_info = estimate_budget(city, duration, budget_type)
        
        st.subheader("Generated Itinerary:")
        st.text(itinerary)
        
        st.subheader("Attraction & Restaurant Recommendations:")
        st.text(recommendations)
        
        st.subheader("Estimated Budget:")
        if "breakdown" in budget_info:
            for key, value in budget_info["breakdown"].items():
                st.text(f"{key.capitalize()}: {value} INR")
            st.text(f"Total Cost: {budget_info['total_cost']} INR")
        
        pdf_filename = "itinerary.pdf"
        generate_pdf(itinerary, recommendations, pdf_filename)
        with open(pdf_filename, "rb") as pdf_file:
            st.download_button("Download Itinerary PDF", pdf_file, file_name=pdf_filename, mime="application/pdf")
    else:
        st.error("Please fill in all fields.")
