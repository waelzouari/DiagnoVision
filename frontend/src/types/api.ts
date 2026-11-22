export type UUID = string;
export interface Doctor { id:UUID; email:string; full_name:string; role?:string }
export interface Patient { id:UUID; full_name:string; date_of_birth:string; sex?:string|null; demographics?:Record<string,string>; medical_history?:string|null; confirmed_conditions?:string[]; allergies?:string[]; medications?:string[]; created_at:string; updated_at?:string }
export interface Observation { id:UUID; patient_id:UUID; code?:string; name:string; value:number|string; unit?:string|null; observed_at:string; status?:'approved'|'draft'; reference_range?:string|null; source_reference?:string|null }
export interface Consultation { id:UUID; patient_id:UUID; mode:string; status:string; occurred_at:string; notes?:string|null; consent_recorded?:boolean; transcript?:Transcript|null; clinical_draft?:ClinicalDraft|null }
export interface Transcript { id:UUID; consultation_id:UUID; original_text:string; corrected_text?:string|null; language?:string; segments?:Array<{start:number;end:number;text:string}>; status:string }
export interface ClinicalFact { label:string; value:string|null; source_reference:string; category?:string; certainty?:string }
export interface ClinicalDraft { id:UUID; consultation_id:UUID; status:string; chief_complaint?:string|null; symptoms?:ClinicalFact[]; negated_symptoms?:ClinicalFact[]; medications?:ClinicalFact[]; allergies?:ClinicalFact[]; observations?:ClinicalFact[]; missing_information?:string[]; recommendations?:string[]; updated_at?:string }
export interface TimelineEvent { id:UUID; type:string; title:string; description?:string; occurred_at:string; status?:string }
export interface Analysis { id:UUID; patient_id:UUID; status:string; summary:string; recent_developments?:string[]; improving?:string[]; stable?:string[]; worsening?:string[]; conflicts?:string[]; references?:string[]; limitations?:string[]; model_version:string; created_at:string; reviewed_at?:string|null }
export interface DocumentRecord { id:UUID; patient_id:UUID; filename:string; content_type:string; status:string; created_at:string; extracted_text?:string|null; observations?:ClinicalFact[] }
export interface Job { id?:UUID; job_id?:UUID; status:'pending'|'processing'|'completed'|'failed'|'cancelled'; progress?:number; result_id?:UUID; error?:string|null; kind?:string }
export interface DashboardOverview { patient_count:number; recent_consultations:Consultation[]; pending_reviews:number; latest_analyses:Analysis[]; relevant_observations:Observation[] }
export interface Paginated<T> { items:T[]; total:number; page:number; page_size:number }
export interface Settings { analysis_frequency:string; language:string; demo_mode:boolean; transcription_language:string; retention_days:number }
