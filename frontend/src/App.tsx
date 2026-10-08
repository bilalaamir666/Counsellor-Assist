import { useEffect, useState } from "react";
import "./App.css";
import Chat from "./pages/Chat";
import Enquiries from "./pages/Enquiries";
import Documents from "./pages/Documents";
import Conversations from "./pages/Conversations";

const API_URL = "http://localhost:8000";

type Stats = {
  status_counts: {
    status: string;
    count: number;
  }[];
  new_per_week: {
    week: string;
    count: number;
  }[];
  top_courses: {
    course: string;
    count: number;
  }[];
  average_days_new_to_applied: number;
};

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [token, setToken] = useState<string | null>(
    localStorage.getItem("access_token")
  );

  const [role, setRole] = useState<string | null>(
    localStorage.getItem("role")
  );

  const [stats, setStats] = useState<Stats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);

  const [currentPage, setCurrentPage] = useState("dashboard");

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Login failed");
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("role", data.role);

      setToken(data.access_token);
      setRole(data.role);
      setCurrentPage("dashboard");
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("role");

    setToken(null);
    setRole(null);
    setStats(null);
    setCurrentPage("dashboard");
  };

  useEffect(() => {
    if (!token || role !== "admin") {
      return;
    }

    const fetchStats = async () => {
      setStatsLoading(true);

      try {
        const response = await fetch(`${API_URL}/stats/enquiries`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to load dashboard statistics");
        }

        const data = await response.json();
        setStats(data);
      } catch (err) {
        console.error(err);
      } finally {
        setStatsLoading(false);
      }
    };

    fetchStats();
  }, [token, role]);

  if (!token) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="login-header">
            <div className="logo-circle">CA</div>

            <h1>Counsellor Assist</h1>

            <p>AI-powered student counselling assistant</p>
          </div>

          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <label htmlFor="email">Email</label>

              <input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>

              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button
              type="submit"
              className="login-button"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="login-footer">
            Admin & Counsellor Portal
          </div>
        </div>
      </div>
    );
  }

  const getPageTitle = () => {
    switch (currentPage) {
      case "chat":
        return "AI Chat";

      case "conversations":
        return "Conversation History";

      case "enquiries":
        return "Student Enquiries";

      case "documents":
        return "Documents";

      default:
        return "Dashboard";
    }
  };

  const getPageDescription = () => {
    switch (currentPage) {
      case "chat":
        return "Ask questions using the university reference documents";

      case "conversations":
        return "View previous AI counselling conversations";

      case "enquiries":
        return "Manage and track student counselling enquiries";

      case "documents":
        return "Manage university reference documents";

      default:
        return "Welcome to Counsellor Assist";
    }
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-small">CA</div>

          <div>
            <strong>Counsellor</strong>
            <span>Assist</span>
          </div>
        </div>

        <nav className="navigation">
          <button
            className={`nav-item ${
              currentPage === "dashboard" ? "active" : ""
            }`}
            onClick={() => setCurrentPage("dashboard")}
          >
            <span>📊</span>
            Dashboard
          </button>

          <button
            className={`nav-item ${
              currentPage === "chat" ? "active" : ""
            }`}
            onClick={() => setCurrentPage("chat")}
          >
            <span>💬</span>
            Chat
          </button>

          <button
            className={`nav-item ${
              currentPage === "conversations" ? "active" : ""
            }`}
            onClick={() => setCurrentPage("conversations")}
          >
            <span>🕘</span>
            Conversations
          </button>

          <button
            className={`nav-item ${
              currentPage === "enquiries" ? "active" : ""
            }`}
            onClick={() => setCurrentPage("enquiries")}
          >
            <span>👨‍🎓</span>
            Enquiries
          </button>

          {role === "admin" && (
            <button
              className={`nav-item ${
                currentPage === "documents" ? "active" : ""
              }`}
              onClick={() => setCurrentPage("documents")}
            >
              <span>📄</span>
              Documents
            </button>
          )}
        </nav>

        <div className="sidebar-bottom">
          <div className="user-info">
            <div className="user-avatar">
              {role === "admin" ? "A" : "C"}
            </div>

            <div>
              <strong>
                {role === "admin" ? "Administrator" : "Counsellor"}
              </strong>

              <span>{role}</span>
            </div>
          </div>

          <button className="logout-button" onClick={handleLogout}>
            🚪 Logout
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>{getPageTitle()}</h1>

            <p>{getPageDescription()}</p>
          </div>

          <div className="role-badge">{role}</div>
        </header>

        {currentPage === "chat" ? (
          <Chat />
        ) : currentPage === "conversations" ? (
          <Conversations />
        ) : currentPage === "enquiries" ? (
          <Enquiries />
        ) : currentPage === "documents" ? (
          role === "admin" ? (
            <Documents />
          ) : (
            <section className="counsellor-welcome">
              <div className="welcome-card">
                <div className="welcome-icon">🔒</div>

                <h2>Access Denied</h2>

                <p>
                  Only administrators can manage reference documents.
                </p>
              </div>
            </section>
          )
        ) : role === "admin" ? (
          <section className="dashboard">
            {statsLoading && (
              <div className="loading-card">
                Loading dashboard statistics...
              </div>
            )}

            {stats && (
              <>
                <div className="stats-grid">
                  <StatCard
                    title="Total Enquiries"
                    value={getTotalEnquiries(stats)}
                    icon="👥"
                  />

                  <StatCard
                    title="New"
                    value={getStatusCount(stats, "new")}
                    icon="🆕"
                  />

                  <StatCard
                    title="Applied"
                    value={getStatusCount(stats, "applied")}
                    icon="📝"
                  />

                  <StatCard
                    title="Closed"
                    value={getStatusCount(stats, "closed")}
                    icon="✅"
                  />
                </div>

                <div className="dashboard-grid">
                  <div className="dashboard-card">
                    <div className="card-header">
                      <div>
                        <h2>New Enquiries</h2>
                        <p>Last 8 weeks</p>
                      </div>
                    </div>

                    <div className="weekly-chart">
                      {stats.new_per_week.map((item) => {
                        const max =
                          Math.max(
                            ...stats.new_per_week.map(
                              (week) => week.count
                            )
                          ) || 1;

                        const height =
                          (item.count / max) * 160;

                        return (
                          <div
                            className="chart-column"
                            key={item.week}
                          >
                            <span className="chart-value">
                              {item.count}
                            </span>

                            <div
                              className="chart-bar"
                              style={{
                                height: `${Math.max(
                                  height,
                                  8
                                )}px`,
                              }}
                            ></div>

                            <span className="chart-label">
                              {item.week}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div className="dashboard-card">
                    <div className="card-header">
                      <div>
                        <h2>Top Courses</h2>
                        <p>Most enquiries</p>
                      </div>
                    </div>

                    <div className="course-list">
                      {stats.top_courses.map(
                        (course, index) => (
                          <div
                            className="course-row"
                            key={course.course}
                          >
                            <div className="course-rank">
                              {index + 1}
                            </div>

                            <div className="course-name">
                              {course.course}
                            </div>

                            <strong>
                              {course.count}
                            </strong>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                </div>

                <div className="dashboard-card average-card">
                  <div>
                    <h2>Average New → Applied</h2>

                    <p>
                      Average time taken for an enquiry to
                      reach the applied stage
                    </p>
                  </div>

                  <div className="average-value">
                    {stats.average_days_new_to_applied}
                    <span>days</span>
                  </div>
                </div>
              </>
            )}
          </section>
        ) : (
          <section className="counsellor-welcome">
            <div className="welcome-card">
              <div className="welcome-icon">👋</div>

              <h2>Welcome, Counsellor</h2>

              <p>
                Use the navigation to chat with the AI
                assistant or manage student enquiries.
              </p>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon,
}: {
  title: string;
  value: number;
  icon: string;
}) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>

      <div>
        <p>{title}</p>
        <h2>{value}</h2>
      </div>
    </div>
  );
}

function getTotalEnquiries(stats: Stats) {
  return stats.status_counts.reduce(
    (total, item) => total + item.count,
    0
  );
}

function getStatusCount(stats: Stats, status: string) {
  return (
    stats.status_counts.find(
      (item) => item.status === status
    )?.count || 0
  );
}

export default App;