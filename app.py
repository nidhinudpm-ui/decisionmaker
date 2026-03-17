from flask import Flask, request, jsonify, send_from_directory
import os
from config import Config
from models.schemas import db, Decision, Option, Criterion, CriterionScore
from services.scoring_service import normalize_scores, calculate_weighted_totals
from services.pdf_service import extract_text_from_pdf
from services.ai_service import get_ai_scores
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='frontend')
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('frontend', 'style.css')

@app.route('/api/decisions', methods=['POST'])
def create_decision():
    data = request.json
    new_decision = Decision(goal=data['goal'])
    db.session.add(new_decision)
    db.session.flush() # Get the ID
    
    # Add Criteria
    for crit in data['criteria']:
        new_crit = Criterion(
            decision_id=new_decision.id,
            name=crit['name'],
            weight=crit['weight'],
            type=crit['type'],
            direction=crit['direction']
        )
        db.session.add(new_crit)
        
    # Add Options
    for opt_name in data['options']:
        new_opt = Option(decision_id=new_decision.id, name=opt_name)
        db.session.add(new_opt)
        
    db.session.commit()
    
    # Ensure upload directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        
    return jsonify({"decision_id": new_decision.id, "message": "Decision created successfully"}), 201

@app.route('/api/decisions/<int:decision_id>/scores', methods=['POST'])
def submit_manual_scores(decision_id):
    data = request.json # List of {option_id, criterion_id, raw_value}
    
    for score_entry in data:
        # Check if score already exists to update or create
        existing_score = CriterionScore.query.filter_by(
            option_id=score_entry['option_id'],
            criterion_id=score_entry['criterion_id']
        ).first()
        
        if existing_score:
            existing_score.raw_value = score_entry['raw_value']
        else:
            new_score = CriterionScore(
                option_id=score_entry['option_id'],
                criterion_id=score_entry['criterion_id'],
                raw_value=score_entry['raw_value']
            )
            db.session.add(new_score)
            
    db.session.commit()
    return jsonify({"message": "Scores updated"}), 200

@app.route('/api/decisions/<int:decision_id>/process-docs', methods=['POST'])
def process_option_documents(decision_id):
    decision = Decision.query.get_or_404(decision_id)
    files = request.files # {option_id: file_placeholder}
    
    results = []
    for opt_id_str, file in files.items():
        opt_id = int(opt_id_str)
        option = Option.query.get(opt_id)
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{decision_id}_{opt_id}_{filename}")
            file.save(file_path)
            
            # Extract Text
            text = extract_text_from_pdf(file_path)
            if text:
                # LLM Scoring
                criteria_list = [{"id": c.id, "name": c.name, "direction": c.direction} for c in decision.criteria]
                scores = get_ai_scores(option.name, text, criteria_list)
                
                if scores:
                    extracted_scores = scores.get('scores', {})
                    rationales = scores.get('rationales', {})
                    
                    for crit_id_str, raw_val in extracted_scores.items():
                        crit_id = int(crit_id_str)
                        rationale = rationales.get(crit_id_str, "")
                        
                        # Save/Update Score
                        existing_score = CriterionScore.query.filter_by(option_id=opt_id, criterion_id=crit_id).first()
                        if existing_score:
                            existing_score.raw_value = float(raw_val)
                            existing_score.evidence_text = rationale
                        else:
                            new_score = CriterionScore(
                                option_id=opt_id, 
                                criterion_id=crit_id, 
                                raw_value=float(raw_val),
                                evidence_text=rationale
                            )
                            db.session.add(new_score)
                    results.append({"option": option.name, "status": "success"})
    
    db.session.commit()
    return jsonify({"message": "Documents processed and scores extracted", "results": results}), 200

@app.route('/api/decisions/<int:decision_id>/results', methods=['GET'])
def get_results(decision_id):
    decision = Decision.query.get_or_404(decision_id)
    
    # Prepare data for scoring service
    criteria_configs = [{"id": c.id, "direction": c.direction} for c in decision.criteria]
    criteria_weights = {c.id: c.weight for c in decision.criteria}
    
    options_data = {}
    options_evidence = {}
    for opt in decision.options:
        options_data[opt.id] = {s.criterion_id: s.raw_value for s in opt.scores}
        options_evidence[opt.id] = {s.criterion_id: s.evidence_text for s in opt.scores}
        
    # 1. Normalize
    normalized_scores = normalize_scores(criteria_configs, options_data)
    
    # 2. Update DB with normalized scores for reference
    for opt_id, scores in normalized_scores.items():
        for crit_id, norm_score in scores.items():
            score_record = CriterionScore.query.filter_by(option_id=opt_id, criterion_id=crit_id).first()
            if score_record:
                score_record.score = norm_score
    db.session.commit()
    
    # 3. Calculate Totals
    rankings = calculate_weighted_totals(criteria_weights, normalized_scores)
    
    # Enrich rankings with option names and rationales
    for rank in rankings:
        opt = Option.query.get(rank['option_id'])
        rank['name'] = opt.name
        # Add rationales for each criterion
        rank['rationales'] = {
            # Find criterion name for UI
            Criterion.query.get(c_id).name: options_evidence[opt.id].get(c_id)
            for c_id in options_evidence[opt.id]
        }
        
    return jsonify({
        "goal": decision.goal,
        "rankings": rankings
    })

if __name__ == '__main__':
    with app.app_context():
        try:
            print(f"Connecting to database at: {app.config['SQLALCHEMY_DATABASE_URI']}")
            db.create_all()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Database initialization failed: {e}")
            print("Attempting to fallback to local SQLite...")
            db_path = os.path.join(os.getcwd(), 'data', 'decision_ai.db')
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
            db.create_all()
            print(f"Fallback SQLite initialized at {db_path}.")
            
    app.run(debug=True, port=8080)
