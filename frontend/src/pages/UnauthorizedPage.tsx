import { Link } from "react-router-dom";

export function UnauthorizedPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-300">403</h1>
        <p className="mt-4 text-xl text-gray-700">Access Denied</p>
        <p className="mt-2 text-gray-500">
          You don&apos;t have permission to access this page.
        </p>
        <Link
          to="/dashboard"
          className="mt-6 inline-block text-primary-600 hover:text-primary-500 font-medium"
        >
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
