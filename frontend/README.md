
## Features


- **User Authentication** - Secure login and signup with role-based access (regular users and VHT workers)
- **Personalized Onboarding** - Collect user health data, dietary preferences, and nutrition goals
- **Nutrition Chat** - AI-powered chatbot for personalized nutrition advice and recommendations
- **Meal Planning** - Generate customized meal plans based on user profile and preferences
- **Daily Food Logging** - Track daily food intake and nutritional metrics
- **Food Explorer** - Browse local foods with detailed nutritional information
- **Nutrition Dashboard** - View health metrics, progress tracking, and insights
- **VHT Dashboard** - Village Health Team worker interface for managing patient groups
- **User Profile Management** - Update personal information and health goals

## Tech Stack

- **Frontend Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **HTTP Client:** Fetch API
- **State Management:** React Hooks
- **UI Components:** Custom React components

## Project Structure

```
src/
├── components/          # React components
│   ├── Auth.tsx        # Login and signup
│   ├── Onboarding.tsx  # User onboarding flow
│   ├── Profile.tsx     # User profile management
│   ├── NutritionChat.tsx   # AI chatbot interface
│   ├── MealPlanner.tsx     # Meal plan generation
│   ├── DailyLogger.tsx     # Food intake logging
│   ├── FoodExplorer.tsx    # Food database browser
│   ├── VHTDashboard.tsx    # VHT worker interface
│   ├── UI.tsx          # Reusable UI components
│   └── App.tsx         # Main app component
├── services/           # API service layer
│   └── apiService.ts   # Backend API calls
├── types.ts            # TypeScript type definitions
├── main.tsx            # React entry point
├── index.css           # Global styles
└── vite-env.d.ts       # Vite environment types
```

## Environment Setup

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create a `.env.local` file in the root directory:**
   ```
   VITE_API_BASE_URL=http://127.0.0.1:8000/api
   ```

   **Environment Variables:**
   - `VITE_API_BASE_URL` - Backend API base URL (default: `http://127.0.0.1:8000/api`)

4. **Start the development server:**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Backend Integration

This frontend connects to a Django backend API. Ensure the backend is running on the configured `VITE_API_BASE_URL` before starting the frontend.

**Key API Endpoints:**
- `/token/` - User authentication
- `/signup/` - User registration
- `/dashboard/` - User dashboard data
- `/onboarding/` - Onboarding data submission
- `/chat/` - Nutrition chat/advice
- `/meal-plan/` - Meal plan generation
- `/logs/` - Daily food logs
- `/vht/dashboard/` - VHT dashboard
- `/vht/register-user/` - Register users (VHT only)



### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run type-check` - Run TypeScript type checking (if configured)
