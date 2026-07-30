// This module owns route protection and keeps public and authenticated screens separate.
import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { AppLayout } from "../layouts/AppLayout";
import { Loading } from "../components/ui";
const LoginPage = lazy(() => import("../pages/AuthPages").then((module) => ({ default: module.LoginPage })));
const RegisterPage = lazy(() => import("../pages/AuthPages").then((module) => ({ default: module.RegisterPage })));
const ResetPasswordPage = lazy(() => import("../pages/AuthPages").then((module) => ({ default: module.ResetPasswordPage })));
const HomePage = lazy(() => import("../pages/MarketingPages").then((module) => ({ default: module.HomePage })));
const AboutPage = lazy(() => import("../pages/MarketingPages").then((module) => ({ default: module.AboutPage })));
const FeaturesPage = lazy(() => import("../pages/MarketingPages").then((module) => ({ default: module.FeaturesPage })));
const ContactPage = lazy(() => import("../pages/MarketingPages").then((module) => ({ default: module.ContactPage })));
const FaqPage = lazy(() => import("../pages/MarketingPages").then((module) => ({ default: module.FaqPage })));
const DashboardPage = lazy(() => import("../pages/DashboardPage").then((module) => ({ default: module.DashboardPage })));
const PredictionsPage = lazy(() => import("../pages/PredictionsPage").then((module) => ({ default: module.PredictionsPage })));
const FarmsPage = lazy(() => import("../pages/FarmsPage").then((module) => ({ default: module.FarmsPage })));
const ReportsPage = lazy(() => import("../pages/OperationsPages").then((module) => ({ default: module.ReportsPage })));
const TrainingPage = lazy(() => import("../pages/OperationsPages").then((module) => ({ default: module.TrainingPage })));
const AnalyticsPage = lazy(() => import("../pages/OperationsPages").then((module) => ({ default: module.AnalyticsPage })));
const ProfilePage = lazy(() => import("../pages/OperationsPages").then((module) => ({ default: module.ProfilePage })));
const SettingsPage = lazy(() => import("../pages/OperationsPages").then((module) => ({ default: module.SettingsPage })));
const NotFoundPage = lazy(() => import("../pages/OperationsPages").then((module) => ({ default: module.NotFoundPage })));
function Protected() { const { user, loading } = useAuth(); if (loading) return <Loading label="Restoring session" />; return user ? <AppLayout /> : <Navigate to="/login" replace />; }
export function AppRoutes() { return <Suspense fallback={<Loading label="Loading page" />}><Routes><Route path="/" element={<HomePage />} /><Route path="/home" element={<HomePage />} /><Route path="/about" element={<AboutPage />} /><Route path="/features" element={<FeaturesPage />} /><Route path="/contact" element={<ContactPage />} /><Route path="/faq" element={<FaqPage />} /><Route path="/login" element={<LoginPage />} /><Route path="/register" element={<RegisterPage />} /><Route path="/forgot-password" element={<LoginPage forgot />} /><Route path="/reset-password" element={<ResetPasswordPage />} /><Route element={<Protected />}><Route path="/dashboard" element={<DashboardPage />} /><Route path="/predictions" element={<PredictionsPage />} /><Route path="/farms" element={<FarmsPage />} /><Route path="/reports" element={<ReportsPage />} /><Route path="/training" element={<TrainingPage />} /><Route path="/analytics" element={<AnalyticsPage />} /><Route path="/profile" element={<ProfilePage />} /><Route path="/settings" element={<SettingsPage />} /></Route><Route path="*" element={<NotFoundPage />} /></Routes></Suspense>; }
