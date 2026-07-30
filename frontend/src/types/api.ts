// These types mirror the FastAPI response contracts and prevent UI/API drift.
export interface User { id: number; email: string; full_name: string | null; is_active: boolean; created_at: string; }
export interface TokenResponse { access_token: string; refresh_token?: string | null; token_type: "bearer"; expires_in: number; }
export interface Farm { id: number; user_id: number; farm_name: string; latitude: number; longitude: number; crop: string | null; area: number | null; is_active: boolean; created_at: string; updated_at: string; }
export interface Recommendation { category: string; message: string; priority: "high" | "medium" | "low"; }
export interface Prediction { id: number; farm_id: number | null; latitude: number; longitude: number; prediction_date: string; drought_index: number; ndvi: number; lst: number; climate: Record<string, number> | null; credit_score: number; risk_classification: string; recommendations: Recommendation[] | null; created_at: string; }
export interface PredictionResult { prediction_id: number; date: string; lat: number; lon: number; predicted_drought_index: number; ndvi: number; lst: number; farmer_score: string; credit_score: number; climate: Record<string, number>; recommendations: Recommendation[]; ndvi_trend: { date: string; ndvi: number }[]; lst_trend: { date: string; lst: number }[]; }
export interface Dashboard { total_predictions: number; average_credit_score: number; high_risk_farms: number; healthy_farms: number; average_ndvi: number; average_temperature: number; }
export interface Analytics { prediction_trends: { date: string; predictions: number; average_credit_score: number; average_ndvi: number }[]; }
export interface ForecastDay { date: string; temperature: number; rainfall: number; humidity: number; wind_speed: number; }
export interface Forecast { latitude: number; longitude: number; days: ForecastDay[]; }
