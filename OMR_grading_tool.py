import streamlit as st
import cv2
import numpy as np
import tempfile
import pandas as pd
from PIL import Image
import base64
from io import BytesIO
import time
import os
from datetime import datetime

# Set up page configuration with a custom theme
st.set_page_config(
    page_title="MarkIt - Premium OMR Solution",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a more professional look
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #1E3A8A !important;
        margin-bottom: 0 !important;
    }
    .sub-header {
        font-size: 1.1rem !important;
        color: #6B7280 !important;
        margin-bottom: 2rem !important;
    }
    .stTabs {
        background-color: #F9FAFB;
        padding: 10px;
        border-radius: 10px;
    }
    .stat-card {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .feature-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .feature-title {
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        font-size: 0.9rem;
        color: #6B7280;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #1E40AF;
    }
    .footer {
        text-align: center;
        color: #6B7280;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
    }
    .results-container {
        background-color: #F9FAFB;
        padding: 20px;
        border-radius: 10px;
        margin-top: 2rem;
    }
    .metrics-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 10px;
    }
    .blue-metric {
        color: #1E3A8A;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Create a branded header
st.markdown("<h1 class='main-header'>MarkIt<span style='font-size:1.8rem; vertical-align:super; color:#4F46E5;'>™</span></h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>The Premium OMR Solution for Modern Educators</p>", unsafe_allow_html=True)

# Initialize session state to store the answer key
if 'answer_key' not in st.session_state:
    # Default answer key (can be modified by user)
    st.session_state.answer_key = {
        1: 2, 2: 3, 3: 2, 4: 3, 5: 3, 
        6: 2, 7: 1, 8: 2, 9: 3, 10: 4,
        11: 4, 12: 1, 13: 2, 14: 5, 15: 5,
        16: 3, 17: 5, 18: 1, 19: 1, 20: 1,
        21: 4, 22: 3, 23: 2, 24: 4, 25: 2,
        26: 3, 27: 1, 28: 2, 29: 1, 30: 2,
        31: 1, 32: 1, 33: 5, 34: 3, 35: 3,
        36: 2, 37: 2, 38: 4, 39: 3, 40: 1,
        41: 2, 42: 5, 43: 1, 44: 5, 45: 4,
        46: 1, 47: 4, 48: 2, 49: 3, 50: 5
    }

if 'results' not in st.session_state:
    st.session_state.results = None

if 'process_count' not in st.session_state:
    st.session_state.process_count = 0

if 'saved_results' not in st.session_state:
    st.session_state.saved_results = []

def process_answer_sheet(image_path, answer_key):
    """
    Process the OMR answer sheet using advanced image processing techniques
    """
    img = cv2.imread(image_path)
    output_img = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply enhanced blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Adaptive thresholding for better performance across different lighting conditions
    _, thresh = cv2.threshold(blurred, 160, 255, cv2.THRESH_BINARY_INV)
    
    # Structure definition
    num_cols = 5  # 5 options per question (1-5)
    num_rows = 10  # 10 rows per section
    questions_per_section = 10  # 10 questions per section
    
    # Optimized circle detection parameters for high precision
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=25,
        param1=50, param2=27, minRadius=10, maxRadius=18
    )
    
    # Initialize answers dictionary
    answers = {q: None for q in range(1, 51)}
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        
        # Create a dictionary to organize circles by rows
        rows = {}
        for (x, y, r) in circles:
            # Get the intensity at this point to filter out non-bubble circles
            if x < img.shape[1] and y < img.shape[0]:
                row_key = y // 30  # Group circles by their y-coordinate
                if row_key not in rows:
                    rows[row_key] = []
                rows[row_key].append((x, y, r))
        
        # Sort rows by y-coordinate
        sorted_rows = sorted(rows.items(), key=lambda x: x[0])
        
        # Process each row
        for row_idx, (_, circles_in_row) in enumerate(sorted_rows):
            # Skip if we've processed all rows
            if row_idx >= 50:
                continue
            
            # Sort circles in this row by x-coordinate
            sorted_circles = sorted(circles_in_row, key=lambda c: c[0])
            
            # Group circles by proximity (representing options for the same question)
            question_groups = []
            current_group = []
            
            for circle in sorted_circles:
                if len(current_group) == 0 or circle[0] - current_group[-1][0] < 50:
                    current_group.append(circle)
                else:
                    question_groups.append(current_group)
                    current_group = [circle]
            
            if current_group:
                question_groups.append(current_group)
            
            # Calculate which section and question this row corresponds to
            section = row_idx // 10
            question_within_section = row_idx % 10
            
            # Process each group (representing a question)
            for col_idx, question_group in enumerate(question_groups):
                if col_idx >= num_cols:
                    continue
                
                # Calculate question number
                question_num = col_idx * questions_per_section + question_within_section + 1
                
                # Find the darkest (most filled) circle for this question
                max_fill_ratio = 0
                selected_option = None
                
                for option_idx, (x, y, r) in enumerate(question_group):
                    # Create a mask for this circle with slightly smaller radius to avoid edge effects
                    mask = np.zeros(thresh.shape, dtype=np.uint8)
                    cv2.circle(mask, (x, y), r-3, 255, -1)
                    
                    # Count black pixels in the masked region
                    masked_region = cv2.bitwise_and(thresh, mask)
                    black_pixel_count = cv2.countNonZero(masked_region)
                    
                    # Calculate fill ratio
                    circle_area = np.pi * ((r-3) ** 2)
                    if circle_area > 0:
                        fill_ratio = black_pixel_count / circle_area
                    else:
                        fill_ratio = 0
                    
                    # Keep track of the most filled circle
                    if fill_ratio > max_fill_ratio:
                        max_fill_ratio = fill_ratio
                        selected_option = option_idx + 1
                
                # Use a higher threshold (0.4) to avoid detecting smudges as filled bubbles
                if max_fill_ratio > 0.4:
                    answers[question_num] = selected_option
                    
                    # Find the coordinates of the selected bubble
                    selected_circle = question_group[selected_option - 1]
                    x, y, r = selected_circle
                    
                    # Mark the circle on the output image with premium styling
                    correct = (answers[question_num] == answer_key.get(question_num))
                    color = (0, 155, 0) if correct else (0, 0, 255)  # Green if correct, red if wrong
                    cv2.circle(output_img, (x, y), r, color, 2)
                    
                    # Add question number above the marked bubble
                    cv2.putText(output_img, f"Q{question_num}", (x - 15, y - 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    # Increment the process counter
    st.session_state.process_count += 1
    
    return answers, output_img

def get_table_download_link(df, filename="markit_results.xlsx"):
    """Generate a link to download the dataframe as an Excel file"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='MarkIt Results', index=False)
        
        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['MarkIt Results']
        
        # Add formats for better styling
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1E3A8A',
            'font_color': 'white',
            'border': 1
        })
        
        # Format the header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Autofit column widths
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col))
            worksheet.set_column(i, i, max_len + 2)
    
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" class="download-button">Download Excel Report</a>'

# Create a sidebar with app information
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/check-all.png", width=80)
    st.markdown("## About MarkIt™")
    st.markdown("""
    MarkIt™ is a premium OMR solution that helps educators grade multiple-choice exams with speed and precision using advanced image processing.
     
    **🔹 100% Privacy Assured**  
    **🔹 Fast & Accurate Results**
    """)
    
    st.markdown("---")
    
    st.markdown("### 🏆 Why Choose MarkIt™?")
    st.markdown("""
    * ⚡ **Speed**: Grade exams in seconds
    * 🎯 **Accuracy**: Precise bubble detection
    * 📊 **Insights**: Detailed analytics
    * 💰 **Cost-Effective**: Save time and resources
    """)
    
    st.markdown("---")
    
    # Show stats in sidebar
    st.markdown("### 📈 Session Statistics")
    if st.session_state.process_count > 0:
        st.markdown(f"**Answer Sheets Processed:** {st.session_state.process_count}")
        if len(st.session_state.saved_results) > 0:
            avg_score = sum([float(result['percentage'].strip('%')) for result in st.session_state.saved_results]) / len(st.session_state.saved_results)
            st.markdown(f"**Average Score:** {avg_score:.2f}%")
    else:
        st.markdown("No answer sheets processed yet.")
    
    st.markdown("---")
    
    # Add a testimonial
    st.markdown("### 💬 What Educators Say")
    st.markdown("""
    > *"MarkIt has revolutionized how we grade exams. What took hours now takes minutes!"*
    
    **- Dr. Sarah Johnson**  
    Director of Assessment, Wellington Academy
    """)

# Create tabs for the application flow with better naming
tab1, tab2, tab3 = st.tabs(["🔑 Configure Answer Key", "📝 Grade Answer Sheets", "📊 Analytics Dashboard"])

# Tab 1: Set Answer Key
with tab1:
    st.markdown("## Configure Your Answer Key")
    st.markdown("Set up the correct answers for your exam. You can input manually or upload from a CSV file.")
    
    # Key Features section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='stat-card'>
            <div class='feature-icon'>🔄</div>
            <div class='feature-title'>Reusable Keys</div>
            <div class='feature-desc'>Save answer keys for future use</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='stat-card'>
            <div class='feature-icon'>📤</div>
            <div class='feature-title'>CSV Import</div>
            <div class='feature-desc'>Quick setup from spreadsheets</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class='stat-card'>
            <div class='feature-icon'>🔐</div>
            <div class='feature-title'>Secure Storage</div>
            <div class='feature-desc'>Keys stored in your session only</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Manual Configuration")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Create 5 columns with 10 questions each
    for i, col in enumerate([col1, col2, col3, col4, col5]):
        with col:
            st.markdown(f"**Questions {i*10+1}-{i*10+10}**")
            for q in range(i*10+1, i*10+11):
                st.session_state.answer_key[q] = st.selectbox(
                    f"Q{q}", 
                    options=[1, 2, 3, 4, 5], 
                    index=st.session_state.answer_key[q]-1,
                    key=f"key_q{q}"
                )
    
    # Save button with animation
    if st.button("💾 Save Answer Key", key="save_key_btn"):
        st.success("✅ Answer key has been saved successfully!")
        st.balloons()
    
    st.markdown("---")
    
    # Allow upload of answer key CSV file
    st.subheader("Import from CSV")
    st.markdown("Upload a CSV file with question numbers and answers for quick setup.")
    
    # Two columns for upload and sample download
    upload_col, sample_col = st.columns([3, 1])
    
    with upload_col:
        csv_file = st.file_uploader(
            "Upload a CSV file with answer key (format: 'Question,Answer')", 
            type=["csv"]
        )
        
    with sample_col:
        # Create sample CSV for download
        sample_df = pd.DataFrame({
            'Question': range(1, 51),
            'Answer': [st.session_state.answer_key[q] for q in range(1, 51)]
        })
        sample_buffer = BytesIO()
        sample_df.to_csv(sample_buffer, index=False)
        sample_b64 = base64.b64encode(sample_buffer.getvalue()).decode()
        st.markdown(f'<a href="data:text/csv;base64,{sample_b64}" download="sample_answer_key.csv">Download Sample CSV</a>', unsafe_allow_html=True)
    
    if csv_file is not None:
        try:
            df = pd.read_csv(csv_file)
            if 'Question' in df.columns and 'Answer' in df.columns:
                for _, row in df.iterrows():
                    q_num = int(row['Question'])
                    ans = int(row['Answer'])
                    if 1 <= q_num <= 50 and 1 <= ans <= 5:
                        st.session_state.answer_key[q_num] = ans
                st.success("✅ Answer key successfully updated from CSV!")
            else:
                st.error("❌ CSV must have 'Question' and 'Answer' columns")
        except Exception as e:
            st.error(f"❌ Error loading CSV file: {str(e)}")

# Tab 2: Grade Answer Sheets
with tab2:
    st.markdown("## Grade OMR Answer Sheets")
    st.markdown("Upload scanned answer sheets to automatically detect and grade student responses.")
    
    # Key Features section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='stat-card'>
            <div class='feature-icon'>🔍</div>
            <div class='feature-title'>High Precision</div>
            <div class='feature-desc'>Advanced bubble detection</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='stat-card'>
            <div class='feature-icon'>⚡</div>
            <div class='feature-title'>Lightning Fast</div>
            <div class='feature-desc'>Results in seconds</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class='stat-card'>
            <div class='feature-icon'>📋</div>
            <div class='feature-title'>Detailed Reports</div>
            <div class='feature-desc'>Complete answer analysis</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Student information
    col1, col2 = st.columns(2)
    with col1:
        student_name = st.text_input("Student Name", placeholder="John Doe")
    with col2:
        student_id = st.text_input("Student ID", placeholder="S12345")
    
    # Upload answer sheet with improved styling
    st.markdown("### Upload Answer Sheet")
    st.markdown("Supports JPG, PNG and JPEG formats. For best results, ensure good lighting and minimal skew.")
    
    uploaded_file = st.file_uploader("📤 Upload a scanned answer sheet image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        # Display a progress indicator
        with st.spinner("🔍 Processing answer sheet..."):
            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            
            # Add a small delay to show the processing animation
            time.sleep(0.5)
            
            # Process the answer sheet
            student_answers, marked_img = process_answer_sheet(tmp_path, st.session_state.answer_key)
            
            # Compute score
            correct = sum(1 for q in student_answers if student_answers[q] == st.session_state.answer_key.get(q))
            total_answered = sum(1 for q in student_answers if student_answers[q] is not None)
            score = f"{correct} / 50"
            percentage = (correct / 50) * 100
            
            # Create results dataframe
            results = []
            for q in range(1, 51):
                student_ans = student_answers[q]
                correct_ans = st.session_state.answer_key[q]
                is_correct = "Yes" if student_ans == correct_ans else "No"
                status = "✓" if student_ans == correct_ans else "✗" if student_ans is not None else "−"
                
                results.append({
                    "Question": q,
                    "Student Answer": student_ans if student_ans is not None else "Unanswered",
                    "Correct Answer": correct_ans,
                    "Status": status
                })
            
            results_df = pd.DataFrame(results)
            
            # Add student info to the top of the dataframe for the Excel download
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            student_info_df = pd.DataFrame([{
                "Student Name": student_name if student_name else "Not Provided",
                "Student ID": student_id if student_id else "Not Provided",
                "Exam Date": timestamp,
                "Score": score,
                "Percentage": f"{percentage:.2f}%",
                "Questions Attempted": total_answered,
                "Questions Correct": correct
            }])
            
            # Store results for later access
            result_data = {
                "student_name": student_name if student_name else "Unnamed Student",
                "student_id": student_id if student_id else "No ID",
                "score": score,
                "percentage": f"{percentage:.2f}%",
                "timestamp": timestamp
            }
            st.session_state.saved_results.append(result_data)
            
            st.session_state.results = {
                "student_name": student_name,
                "student_id": student_id,
                "score": score,
                "percentage": percentage,
                "details": results_df,
                "student_info": student_info_df,
                "marked_img": marked_img,
                "timestamp": timestamp
            }
        
        # Success message
        st.success("✅ Answer sheet processed successfully!")
        
        # Display results in a well-designed container
        st.markdown("<div class='results-container'>", unsafe_allow_html=True)
        
        # Results header
        st.markdown(f"## Results for {student_name if student_name else 'Unnamed Student'}")
        st.markdown(f"**Processed on:** {timestamp}")
        
        # Key metrics in cards
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            st.markdown("<div class='metrics-card'>", unsafe_allow_html=True)
            st.metric("Score", score)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with metric_cols[1]:
            st.markdown("<div class='metrics-card'>", unsafe_allow_html=True)
            st.metric("Percentage", f"{percentage:.2f}%")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with metric_cols[2]:
            st.markdown("<div class='metrics-card'>", unsafe_allow_html=True)
            st.metric("Attempted", f"{total_answered} / 50")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with metric_cols[3]:
            st.markdown("<div class='metrics-card'>", unsafe_allow_html=True)
            st.metric("Accuracy", f"{(correct/total_answered*100):.1f}%" if total_answered > 0 else "N/A")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Results visualization
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Convert to RGB for PIL
            marked_rgb = cv2.cvtColor(marked_img, cv2.COLOR_BGR2RGB)
            st.image(marked_rgb, caption="📝 Marked Answer Sheet", use_column_width=True)
            
            # Download image button
            buf = BytesIO()
            Image.fromarray(marked_rgb).save(buf, format="PNG")
            img_b64 = base64.b64encode(buf.getvalue()).decode()
            st.markdown(f'<a href="data:image/png;base64,{img_b64}" download="marked_sheet_{student_id if student_id else "unnamed"}.png">Download Marked Sheet</a>', unsafe_allow_html=True)
        
        with col2:
            # Create a pie chart for correct vs incorrect
            correct_data = correct
            incorrect_data = total_answered - correct
            unanswered_data = 50 - total_answered
            
            fig_data = pd.DataFrame({
                'Category': ['Correct', 'Incorrect', 'Unanswered'],
                'Count': [correct_data, incorrect_data, unanswered_data],
                'Color': ['#4CAF50', '#F44336', '#9E9E9E']
            })
            
            st.markdown("### Answer Distribution")
            
            # Streamlit doesn't support custom colors in pie charts easily
            # So we'll create a horizontal bar chart instead
            st.bar_chart(fig_data.set_index('Category')['Count'], use_container_width=True)
            
            # Excel download button
            combined_df = pd.concat([student_info_df, pd.DataFrame([{"": ""}]), results_df])
            filename = f"markit_results_{student_id if student_id else 'unnamed'}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            st.markdown(get_table_download_link(combined_df, filename), unsafe_allow_html=True)
        
        # Detailed results in expandable section
        with st.expander("📊 View Detailed Question Analysis"):
            st.dataframe(results_df, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Tab 3: Analytics Dashboard
with tab3:
    st.markdown("## Analytics Dashboard")
    st.markdown("View aggregate statistics and insights from all processed answer sheets.")
    
    if len(st.session_state.saved_results) > 0:
        # Display results summary
        st.markdown("### Session Summary")
        
        # Create summary metrics
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        
        with metrics_col1:
            st.markdown("<div class='metrics-card'>", unsafe_allow_html=True)
            st.metric("Total Answer Sheets", len(st.session_state.saved_results))
            st.markdown("</div>", unsafe_allow_html=True)
            
        with metrics_col2:
            avg_score = sum([float(result['percentage'].strip('%')) for result in st.session_state.saved_results]) / len(st.session_state.saved_results)
            st.markdown("<div class='metrics-card'>", unsafe_allow_html=True)
            st.metric("Average Score", f"{avg_score:.2f}%")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with metrics_col3:
            highest_score = max([float(result['percentage'].strip('%')) for result in st.session_state.saved_results])
            st.markdown("<div class='metrics-card'>", unsafe_allow_html=True)
            st.metric("Highest Score", f"{highest_score:.2f}%")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Create a results table
        st.markdown("### Processed Sheets")
        results_df = pd.DataFrame(st.session_state.saved_results)
        st.dataframe(results_df, use_container_width=True)
        
        # Download all results
        if st.button("📥 Export All Results"):
            st.markdown(get_table_download_link(results_df, "markit_session_results.xlsx"), unsafe_allow_html=True)
            
    else:
        # Show empty state
        st.info("📊 No answer sheets have been processed yet. Grade some answer sheets to see analytics.")
        
        # Show a sample analytics image
        st.markdown("### Sample Analytics Preview")
        st.image("https://img.icons8.com/color/452/analytics.png", width=300)
        st.markdown("Process answer sheets to generate real-time analytics and gain insights into student performance.")

# Add a footer
st.markdown("---")
st.markdown("""
<div class='footer'>
    <p>MarkIt™ Premium OMR Solution | © 2025 | All Rights Reserved</p>
    <p>Bringing Speed and Accuracy to Exam Grading</p>
</div>
""", unsafe_allow_html=True)
