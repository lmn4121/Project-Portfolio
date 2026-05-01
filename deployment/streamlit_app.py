GEMINI_API_KEY= ""
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
TAVILY_API_KEY = ""

import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import os 
import pickle
from PIL import Image

import math
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.preprocessing import TargetEncoder
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import torch
import torch.nn as nn

import shap
import streamlit_shap as st_shap

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, WebSearchTool, function_tool
from agents.model_settings import ModelSettings
from openai import OpenAI
from tavily import TavilyClient
from pydantic import BaseModel, Field
import io
import asyncio
import base64

# Function to load the target encoder from training
def load_encoder(filepath = 'target_encoder.pkl'):
    """Loads an encoder from a pickle file."""
    with open(filepath, 'rb') as f:
        encoder = pickle.load(f)
    print(f"Encoder loaded from {filepath}")
    return encoder

# Function to load the robust scaler from training
def load_scaler(filepath = 'robust_scaler.pkl'):
    """Loads an encoder from a pickle file."""
    with open(filepath, 'rb') as f:
        scaler = pickle.load(f)
    print(f"Scaler loaded from {filepath}")
    return scaler

# Function to load the pickle files of pca_models for conversion of new input
def load_pca_models(folder="pca_models"):
    """Reloads all pickle files from a folder into a dictionary."""
    models_dict = {}
    if not os.path.exists(folder):
        print("Folder not found.")
        return models_dict

    for filename in os.listdir(folder):
        if filename.endswith(".pkl"):
            name = filename.replace(".pkl", "")
            filepath = os.path.join(folder, filename)
            with open(filepath, 'rb') as f:
                models_dict[name] = pickle.load(f)
            print(f"Loaded: {name}")
    
    return models_dict

# Reload the cluster features to order new inputs
with open("feat_clusters.pkl", "rb") as f:
    feat_clusters = pickle.load(f)

# Reload all necessary features
with open("all_feats.pkl", "rb") as f:
    all_feats = pickle.load(f)

with open("features_mini.pkl", "rb") as f:
    features_mini = pickle.load(f)
    
# Add the state name to the clusters
feat_clusters.append(['State_Name'])

# Function to process a 14 input dataset for the mini model
def create_processable_df(base):
    # Create a blank matrix of zeros
    frame = pd.DataFrame(0, index=base.index, columns=all_feats)
    
    # Add information from the input
    frame.update(base)

    return frame

# Function to process a csv input
def process_input_data(df):
    # Load the encoder and scaler
    encoder = load_encoder()
    scaler = load_scaler()
    
    # Check that all necessary features are present
    if model_type == full_model and set(all_feats).issubset(list(df.columns)):
        df = df[all_feats]

        # 1. Load the target encoder from training
        # 2. Target encode the state names
        # 3. Load the robust scaler from training
        # 4. Scale the features
        
        # Encoding
        df[['State_Name']] = encoder.transform(df[['State_Name']])
        
        # Scaling
        scaled = scaler.transform(df)
        df = pd.DataFrame(scaled, columns=df.columns)
        
        # Load the pca_models
        pca_models = load_pca_models()
        
        #For each cluster in the feat_clusters
        # 1. Take a cluster of features
        # 2. Take the corresponding pca model
        # 3. Compress the cluster into a single component
        # 4. Add the component to the compressed_data
        # 5. Rename the components for interpretability
        # 6. Append the components into a single DataFrame
        
        compressed_data = []
        for clus in range(len(feat_clusters)):
            pca = pca_models[f'pca_clus_{clus+1}']
            compressed_data.append(pd.DataFrame(pca.transform(df[feat_clusters[clus]])))
        
        # Component names from training
        pc_names = ['Death_Rate', 'Population_And_Marriage', 'Vaccination', 'Population_Urban', 
                'Delivery', 'Foods', 'Death_Rate_Urban', 'Neo_Natal_Mortality', 'Birth_rate', 'Check_Up',
                'Government_Assist', 'BCG_No_Vaccination', 'Illiteracy', 'State']
        
        ## Rename PC groups for interpretability
        for x in range(len(compressed_data)):
            compressed_data[x] = compressed_data[x].rename(columns={0: pc_names[x]})
        
        # Append all of the compenents into a single data frame
        input_features = pd.DataFrame()
        
        for x in range(len(compressed_data)):
            input_features = pd.concat([input_features, compressed_data[x]], axis=1)

    elif model_type == mini_model and set(features_mini).issubset(list(df.columns)):
        # Create a base dataframe that fits the encoder and scaler
        df = create_processable_df(df[features_mini])
        # Encoding
        df[['State_Name']] = encoder.transform(df[['State_Name']])
        
        # Scaling
        scaled = scaler.transform(df)
        df = pd.DataFrame(scaled, columns=df.columns)

        # Extract the featureset
        input_features = df[features_mini]
        
    else:
        st.write('Missing Features!')
        return None
        
    return input_features

# Function to convert a dataframe to a tensor for the model
def df_to_tensor(df):
    """ converts an input df to a PyTorch tensor """
    values = df.values
    tensor = torch.tensor(values, dtype=torch.float)
    return tensor

# Function to make a prediction with a provided model
# Returns the predictions and their corresponding districts
def make_prediction(model, input_tensor, districts):
    preds = model(input_tensor).squeeze(dim=1).tolist()
    preds = pd.DataFrame(preds, columns=['Predicted IMR'])
    ret = pd.concat([districts, preds], axis=1)
    return ret

# Function to generate a shap explanation of a prediction
def shap_exp(model, input_tensor, processed_data, option, districts):
    if model_type==full_model:
        st.markdown("##### Input components of each feature:")
        st.image("cluster_img.png")
    
    explainer = shap.DeepExplainer(model, input_tensor)
    # 1. Get raw SHAP values from your model
    shap_values = explainer.shap_values(input_tensor)

    # 2. Extract the base value
    # For regression, this is usually a single scalar (the average model output)
    base_val = explainer.expected_value
    if isinstance(base_val, (list, np.ndarray)):
        base_val = base_val[0]

    # 3. Handle cases where shap_values_raw is returned as a list [array]
    sv = shap_values[0] if isinstance(shap_values, list) else shap_values

    # 4. Wrap into the Explanation object
    exp = shap.Explanation(
        values=sv.squeeze(),
        base_values=base_val,
        data=input_tensor.cpu().numpy(), # Features for coloring the dots
        feature_names=processed_data.columns      # List of strings (e.g., X.columns)
    )

    idx = districts[districts['District Name'] == option].index[0]
    # Shap explanation of outlier with residual of 0.75
    
    # Waterfall Plot
    fig, ax = plt.subplots()
    shap.plots.waterfall(exp[idx], max_display = len(shap_values[0]), show=False)
    plt.suptitle(f"Prediction Explanation for {option}", y=1.0, x=0.43, fontsize=15)
    st.pyplot(plt.gcf())
    
    # Turns the waterfall plot into an image to be processed by an agent
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    base64_image = base64.b64encode(buf.read()).decode('utf-8')
    plt.show()
    plt.close()

    st.write("###### This plot displays the impact each input had on the IMR prediction for the selected district. For a more detailed breakdown, refer to the agent below:")
    ai_explanation = st.toggle('Generate Agent Interpretation')

    # Runs an explainer agent to explain the SHAP waterfall plot
    if ai_explanation:
        # Extracts information from the SHAP explainer to provide to the agent
        feature_names = exp[idx].feature_names # Names of the features
        feature_values = exp[idx].values # Feature impacts on the prediction
        feature_shap = exp[idx].data # Scaled values of the features
                
        # Creates a context map for the agent to refer to for feature names and values: "Feature_Name: Value, Name: Impact"
        context_map = "\n".join([f"- {name} Value: {shap}, {name} Impact: {val}"
                                 for name, shap, val in zip(feature_names, feature_shap, feature_values)])
        
        asyncio.run(create_AI_explanation(base64_image, context_map)) # Runs the explainer agent function

        st.write("###### Want more information?")
        
        ai_insight = st.toggle('Generate Agent Insight and Report') # An option for a full agent report

        if ai_insight:
            asyncio.run(agentic_insight(context_map, option)) # Runs the full agent report function     

async def create_AI_explanation(base64_image, context_map):
    st.write('Working on an explanation...')
    gemini_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=GEMINI_BASE_URL)
    gemini_model = OpenAIChatCompletionsModel(model="gemini-3.1-flash-lite-preview", openai_client=gemini_client)
    instructions = "You are a Data Science assistant. Analyze the provided SHAP waterfall plot to determine how each feature impacts the predicted Infant Mortality Rate. You are given two values. The first values is the scaled feature value: a positive value indicates a higher measurement, and a negative value indicates a lower measurement. The magnitude represents how high or low the value is. The second value is the feature impact, which describes how the feature affected the prediction."

    # agent that analyzes the SHAP waterfall plot
    img_analyst = Agent(name = "ImageAnalyst",
                    instructions = instructions,
                    model = gemini_model)
    messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image", 
                        "image_url": f"data:image/png;base64,{base64_image}"
                    },
                    {
                        "type": "input_text", 
                        "text": f"""What does this SHAP waterfall plot show about each feature's impact on the final Infant Mortality Rate prediction?

                        For accurate feature identification, use this list of full names and values from the plot: {context_map}
                        
                        Please explain the impact of the top features using their full names.
                        
                        """
                    }
                ]
            }
        ]

    st.write("Agent is analyzing the plot...")
    result = await Runner.run(starting_agent=img_analyst, input=messages) # Gets the agents response/analysis
    
    st.write("\n--- Agent Interpretation ---")
    st.write(result.final_output) # Writes the agents analysis

class WebSearchItem(BaseModel):
    reason: str = Field(
    description = "Your reasoning for why this search is important to explaining what impacts infant mortality rate."
    )
    
    query: str = Field(
    description = "The search term to use for the web search."
    )

tavily = TavilyClient(api_key=TAVILY_API_KEY)

# Search tool for a search agent to use
@function_tool
def search_tavily(query: str) -> str:
    response = tavily.search(query=query, search_depth="advanced", max_results=5)

    results = []
    for result in response['results']:
        results.append(f"Title: {result['title']}\nURL: {result['url']}\nContent: {result['content']}\n")

    return "\n---\n".join(results)

# Object to store the web search queries from the planner agent
class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(
    description = """ A list of web searches to perform to best explain what impacts infant mortality rate."""
    )

# Object to store the final agent report
class ReportData(BaseModel):
    short_summary: str = Field(
    description = """A short 2-3 sentence summary of the findings."""
    )

    markdown_report: str = Field(
    description = """The final report"""
    )

    follow_up_questions: list[str] = Field(
    description = """Suggested topics to research further"""
    )

# function that performs web searches
async def perform_searches(search_agent, search_plan: WebSearchPlan):
    #tasks = [asyncio.create_task(search(item, search_agent)) for item in search_plan.searches]
    #results = await asyncio.gather(*tasks)

    results = []
    for item in search_plan.searches:
        # Run the search
        res = await search(item, search_agent)
        results.append(res) # Store the results
        
        # Add a delay to stay under quota (e.g., 5 seconds for 12 RPM)
        await asyncio.sleep(6)
        
    return results

# Helper function for web searching
async def search(item: WebSearchItem, search_agent):
    input = f"search term: {item.query}\nReason for searching: {item.reason}"
    result = await Runner.run(search_agent, input) # Runs the search agent
    return result.final_output

# Function for writing the final agent report
async def write_report(writer_agent, search_results: list[str]):
    input = f"Summarized search results: {search_results}"
    result = await Runner.run(writer_agent, input) # Runs the writer agent
    return result.final_output
    
# Full function for generating agent insight based on shap values combined with a web search
async def agentic_insight(context_map, district):

    gemini_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=GEMINI_BASE_URL)
    gemini_model = OpenAIChatCompletionsModel(model="gemini-3.1-flash-lite-preview", openai_client=gemini_client)

    # Define a search agent
    # This agent uses provided queries to search the internet
    # combines the search with the SHAP values to provide a report
    INSTRUCTIONS_SEARCH = f"You are a research assistant. Given a search term, you search the web for that term and \
    produce a concise summary of the results. You will then combine the web search results with SHAP value \
    interpretations from {context_map} to suggest potential solutions for reducing infant mortality rate for {district}, a district in India. \
    The provided Shap interpretations include two values, The first values is the scaled feature value: a positive value indicates a higher \
    measurement, and a negative value indicates a lower measurement. The magnitude represents how high or low the value is. The second value \
    is the feature impact, which describes how the feature affected the prediction. \
    The summary must be 1 paragraph and less than 200 words. Capture the main points. Write succintly, no \
    need to have complete sentences or good grammar. This will be consumed by someone synthesizing a \
    report, so it's vital you capture the essence and ignore any fluff."

    search_agent = Agent(name = "SearchAgent",
                         instructions=INSTRUCTIONS_SEARCH,
                         tools=[search_tavily],
                         model=gemini_model,
                         model_settings=ModelSettings(tool_choice="required"))

    # Define a planner agent
    # This agent plans the search queries for the search agent
    HOW_MANY_SEARCHES = 5

    INSTRUCTIONS_PLANNER = f" You are a helpful research assistant. Given a district name and a set of variable names for predicting \
    infant mortality rate, come up with a set of web searches to perform to best explain what is impacting infant mortality rate \
    for the district. Output {HOW_MANY_SEARCHES} terms to query for."

    planner_agent = Agent(name="PlannerAgent",
                          instructions=INSTRUCTIONS_PLANNER,
                          model=gemini_model,
                          output_type=WebSearchPlan)

    # Define a writer agent
    # Writes a report based on the search agent's output
    INSTRUCTIONS_WRITER = (
        f"You are a senior researcher tasked with writing a cohesive report regarding infant mortality rate in {district}."
        "You will be provided with some initial research done by a research assistant.\n"
        "You should first come up with an outline for the report that describes the structre and "
        "flow of the report. Then, generate the report and return that as your final output.\n"
        "The final output should be in markdown format, and it should be detailed. Aim"
        "for at least 250 words."
)
    writer_agent = Agent(name="WriterAgent",
                         instructions=INSTRUCTIONS_WRITER,
                         model=gemini_model,
                         output_type=ReportData)

    st.write('Researching...')

    # Use the planner agent to plan which searches to run
    planner_input = (
        f"Analyze infant mortality rate for the following district: {district}. "
        f"Here are the predictor variables and their impacts:\n{context_map}"
    )

    search_plan = await Runner.run(planner_agent, planner_input)
    # perform searches
    search_results = await perform_searches(search_agent, search_plan.final_output)

    # write the report
    st.write('Writing Report...')
    report = await write_report(writer_agent, search_results)
    st.write("---Agentic Report---")
    st.markdown(report.markdown_report)

# Function to run main pipeline
def runner(df, districts):

    # Define necessary elements
    processed_data = process_input_data(df)
    input_tensor = df_to_tensor(processed_data)

    # Load the requested model
    if model_type == full_model:
        model = torch.load('deployment_model.pth', weights_only = False)
    elif model_type == mini_model:
        model = torch.load('ann_mini.pth', weights_only = False)
        
    # Set the model to evaluation mode    
    model.eval()

    # Make Prediction
    with torch.no_grad():
        results = make_prediction(model, input_tensor, districts)
        
    # Display the predictions
    st.write(""" #### IMR Predictions """)
    st.dataframe(results, hide_index=True)

    # Prediction explanation
    provide_explanations = st.toggle('Prediction Breakdown')
    if provide_explanations:
        option = st.selectbox('Choose a district',
                               tuple(districts['District Name']))
        shap_exp(model, input_tensor, processed_data, option, districts)

def file_upload(uploaded_file=None, template=None):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # preview the uploaded file
        st.write("### Uploaded file preview")
        st.dataframe(df)
        
    elif template is not None:
        df = template

    districts = df[["State_District_Name"]]
    districts = districts.rename(columns={'State_District_Name': 'District Name'})

    runner(df, districts)

# Main

# Define a sidebar (margin)
st.sidebar.title('Model Options')

# Model selection
no_model = "Home"
full_model = 'IMR Predictor (50 Inputs)'
mini_model = 'IMR Predictor-Mini (14 Inputs)'
model_type = st.sidebar.selectbox("Select a Model Type", 
                                  [no_model, full_model, mini_model])

with st.sidebar:
    with st.container(border=True):
        st.write(f'#### {full_model} Metrics:')
        r2_full, rmse_full = st.columns(2)
        r2_full.metric(label="R\u00B2", value="86%")
        rmse_full.metric('Average Error', value="+/-5.1")
    with st.container(border=True):
        st.write(f'#### {mini_model} Metrics:')
        r2_mini, rmse_mini = st.columns(2)
        with r2_mini:
            st.metric(label="R\u00B2", value="84%")
        with rmse_mini:
            st.metric('Average Error', value="+/-5.75")  

supported_states = ['Assam', 'Bihar', 'Chhattisgarh', 'Jharkhand', 'Madhya Pradesh',
       'Odisha', 'Rajasthan', 'Uttar Pradesh', 'Uttarakhand']

if model_type==no_model:
    """ ## Infant Mortality Rate Predictor """
    """ This model will predict the infant mortality rate for a district in one of the supported states.  """
    
    st.write("\n".join([f"- {state}" for state in supported_states]))
    
    """ There are two selectable models. 
    - IMR Predictor model will require more information and makes more accurate predictions
    - IMR Predictor-Mini model requires less information, but the predictions are less accurate... """
else:
    st.write(f"### {model_type} Selected")
    st.write("##### Upload a CSV file (recommended) or enter data manually:")

# Enter data and run model

if 'manual' not in st.session_state:
    st.session_state.manual = False
if 'single_input' not in st.session_state:
    st.session_state.single_input = False

def disable_manual():
    if st.session_state.single_input==True:
        st.session_state.manual=False
def disable_single_input():
    if st.session_state.manual==True:
        st.session_state.single_input=False

file_uploaded=False

if model_type == full_model:
    st.session_state.single_input=False
    template = pd.DataFrame(columns=['State_District_Name']+all_feats)
    
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file == None:
        st.write('Data should match the following template:')
        st.dataframe(template)
    else:
        file_uploaded=True
        file_upload(uploaded_file=uploaded_file)

if model_type == mini_model:
    template = pd.DataFrame(columns=['State_District_Name']+features_mini)
    
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file == None:
        st.write('Data should match the following template (Be sure to include State_District_Name):')
        st.dataframe(template)
    else:
        file_uploaded=True
        file_upload(uploaded_file=uploaded_file)
        
if not file_uploaded and model_type!=no_model:
    st.toggle("Enter Data Manually", key="manual", on_change=disable_single_input)
    if model_type == mini_model:
        single_input=st.toggle("Single Input", key="single_input", on_change=disable_manual)

def submit_manual_df():
    file_upload(template=template)

def submit_single_input():
    file_upload(template=single)

if model_type!=no_model and st.session_state.manual:
    st.data_editor(template, num_rows='dynamic')

single = pd.DataFrame(0, index=[0], columns=features_mini)
if st.session_state.single_input:
    single[['State_District_Name']] = st.text_input('District Name')
    single[['State_Name']] = st.selectbox("State Name", supported_states)
    single[['YY_Crude_Death_Rate_Cdr_Total_Female']] = st.number_input("Female Crude Death Rate (Total)")
    single[['AA_Ever_Married_Women_Aged_15_49_Years_Total']] = st.number_input("Ever Married Women (Ages 15-49)")
    single[['TT_Children_Aged_12_23_Months_Who_Have_Received_3_Doses_Of_Dpt_Vaccine_Total']] = st.number_input("12 to 23 Month Old Children Who Have Recieved 3 Doses of DPT Vaccine")
    single[['AA_Sample_Units_Urban']] = st.number_input("Sample Units (Urban)")
    single[['QQ_Delivery_At_Government_Institution_Rural']] = st.number_input("Delivery at Government Institution (Rural)")
    single[['VV_Children_Who_Received_Foods_Other_Than_Breast_Milk_During_First_6_Months_Vegetables_Fruits_Urban']] = st.number_input("Children Who Receieved Fruits or Vegetables in the First 6 Months (Urban)")
    single[['YY_Crude_Death_Rate_Cdr_Urban_Female']] = st.number_input("Female Crude Death Rate (Urban)")
    single[['YY_Post_Neo_Natal_Mortality_Rate_Total']] = st.number_input("Post Neonatal Mortality Rate")
    single[['ZZ_Crude_Birth_Rate_Total_Upper_Limit']] = st.number_input("Crude Birth Rate (Total Upper Limit)")
    single[['RR_New_Borns_Who_Were_Checked_Up_Within_24_Hrs_Of_Birth_Rural']] = st.number_input("Newborns Checked Up Within 24 Hours of Birth (Rural)")
    single[['PP_Mothers_Who_Received_Anc_From_Govt_Source_Total']] = st.number_input("Mothers Who Received ANC From A Government Source (Total)")
    single[['TT_Children_Aged_12_23_Months_Who_Have_Received_Bcg_Total']] = st.number_input("12 to 23 Month Old Children Who Have Recieved DPT Vaccine (Total)")
    single[['EE_Marriages_Among_Males_Below_Legal_Age_21_Years_Total']] = st.number_input("Marriages Among Males Below the Legal Age (21)")

if model_type!=no_model and (st.session_state.single_input or st.session_state.manual):
    if st.button("Submit"):
        if st.session_state.single_input:
            # 'single' was defined above in your input section
            file_upload(template=single)
        elif st.session_state.manual:
            file_upload(template=template)
        elif file_uploaded:
            file_upload(uploaded_file=uploaded_file)
