import { useEffect, useState } from "react";

import {
  connectGithub,
  getGithubMe,
  getGithubActivity,
  getGithubActivities,
  getWorkSummary,
  syncGithubActivity,
} from "../../api/github";

import { current_user } from "../../api/auth";
import { generatePost } from "../../api/posts";

import { useNavigate } from "react-router-dom";

import {
  Bell,
  Settings,
  ChevronDown,
  CalendarDays,
  Activity,
  Folder,
  Code2,
  GitBranch,
  ArrowRight,
  Sparkles,
} from "lucide-react";

import black_logo from "../../assets/black_logo_logs.png";

import "./Dashboard.css";

const Dashboard = () => {
  const navigate = useNavigate();

  // ============================================================
  // STATE
  // ============================================================

  const [postTime, setPostTime] = useState("");

  const [github, setGithub] = useState(null);

  const [githubActivity, setGithubActivity] = useState(null);

  const [activities, setActivities] = useState([]);

  const [summary, setSummary] = useState(null);

  const [workSummaryId, setWorkSummaryId] = useState(null);

  const [generatedPost, setGeneratedPost] = useState("");

  const [loading, setLoading] = useState(false);

  const [postLoading, setPostLoading] = useState(false);

  const [error, setError] = useState("");

  // ============================================================
  // LOAD DASHBOARD
  // ============================================================

  async function loadDashboard() {
    if (!postTime) {
      setError("Please select your post time.");

      return;
    }

    try {
      setLoading(true);

      setError("");

      // --------------------------------------------------------
      // STEP 1
      // Get GitHub profile
      // Get current GitHub activity
      // Sync GitHub activity to database
      //
      // These can happen in parallel because none of them
      // depends on the result of another one.
      // --------------------------------------------------------

      const [githubData, githubActivityData, syncData] = await Promise.all([
        getGithubMe(),

        getGithubActivity(postTime),

        syncGithubActivity(postTime),
      ]);

      // --------------------------------------------------------
      // STEP 2
      //
      // IMPORTANT:
      //
      // These happen AFTER sync finishes.
      //
      // Therefore retrieve_activity() can see the newly
      // saved activities.
      //
      // And retrieve_summary_llm() can generate a summary
      // from those activities.
      // --------------------------------------------------------

      const [activitiesData, summaryData] = await Promise.all([
        getGithubActivities(postTime),

        getWorkSummary(postTime),
      ]);

      // --------------------------------------------------------
      // Update React state
      // --------------------------------------------------------

      setGithub(githubData);

      setGithubActivity(githubActivityData);

      setActivities(activitiesData);

      setWorkSummaryId(summaryData.work_summary_id);

      setSummary(summaryData.llm_summary);

      // Clear previous generated post
      setGeneratedPost("");
    } catch (error) {
      console.error("Dashboard error:", error);

      if (error.response) {
        setError(error.response.data?.detail || "Could not load dashboard");
      } else {
        setError("Could not connect to the server");
      }
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // CREATE POST
  // ============================================================

  async function createPost() {
    if (!workSummaryId) {
      setError("Load your dashboard summary before creating a post.");

      return;
    }

    try {
      setPostLoading(true);

      setError("");

      const data = await generatePost(workSummaryId);

      setGeneratedPost(data.post);
    } catch (error) {
      console.error("Post generation error:", error);

      if (error.response) {
        setError(error.response.data?.detail || "Could not generate post");
      } else {
        setError("Could not connect to the server");
      }
    } finally {
      setPostLoading(false);
    }
  }

  // ============================================================
  // CHECK SESSION
  // ============================================================

  useEffect(() => {
    checkSession();
  }, []);

  async function checkSession() {
    try {
      // --------------------------------------------------------
      // Check LOGS authentication
      // --------------------------------------------------------

      await current_user();

      // --------------------------------------------------------
      // Check GitHub connection
      // --------------------------------------------------------

      await checkGithubConnection();
    } catch (error) {
      navigate("/auth");
    }
  }

  // ============================================================
  // CHECK GITHUB CONNECTION
  // ============================================================

  async function checkGithubConnection() {
    try {
      const data = await getGithubMe();

      setGithub(data);
    } catch (error) {
      setGithub(null);
    }
  }

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="dashboard">
      {/* ======================================================
          NAVBAR
      ====================================================== */}

      <header className="dashboard-nav">
        {/* BRAND */}

        <div className="brand">
          <div className="brand-icon">
            <img src={black_logo} alt="LOGS" />
          </div>

          <span>LOGS</span>
        </div>

        {/* NAVIGATION */}

        <nav>
          <button className="nav-active">Overview</button>

          <button>Create</button>

          <button>History</button>
        </nav>

        {/* RIGHT SIDE */}

        <div className="nav-right">
          <Bell size={20} strokeWidth={1.8} />

          <Settings size={20} strokeWidth={1.8} />

          {/* --------------------------------------------------
              GITHUB PROFILE
              -------------------------------------------------- */}

          {github ? (
            <div className="profile">
              {github.avatar_url ? (
                <img src={github.avatar_url} alt="" />
              ) : (
                <div className="profile-letter">
                  {github.username?.[0]?.toUpperCase()}
                </div>
              )}

              <span>{github.username}</span>

              <ChevronDown size={16} />
            </div>
          ) : (
            <button className="connect-github-button" onClick={connectGithub}>
              <GitBranch size={17} />
              Connect GitHub
            </button>
          )}
        </div>
      </header>

      {/* ======================================================
          TIME SELECTOR
      ====================================================== */}

      <div className="dashboard-controls">
        <label>Post time</label>

        <input
          type="time"
          value={postTime}
          onChange={(e) => setPostTime(e.target.value)}
        />

        <button
          className="load-button"
          onClick={loadDashboard}
          disabled={loading}
        >
          {loading ? "Loading..." : "Load dashboard"}
        </button>
      </div>

      {/* ERROR */}

      {error && <div className="dashboard-error">{error}</div>}

      {/* ======================================================
          DASHBOARD CONTENT
      ====================================================== */}

      {!summary && !loading ? (
        <div className="empty-dashboard">
          <h2>Ready when you are.</h2>

          <p>Choose your post time to load your work summary.</p>
        </div>
      ) : (
        <main className="dashboard-grid">
          {/* ==================================================
              MAIN SUMMARY CARD
          ================================================== */}

          <section className="summary-card">
            <div className="summary-header">
              <div>
                <p className="eyebrow">TODAY</p>

                <h1>Your work, remembered.</h1>

                <p className="subtitle">
                  LOGS analyzed your activity and generated this summary.
                </p>
              </div>

              <div className="date-pill">
                <CalendarDays size={17} />

                <span>Today</span>
              </div>
            </div>

            {/* AI SUMMARY */}

            {summary?.summary && (
              <div className="ai-summary">{summary.summary}</div>
            )}

            {/* ==================================================
                STATS
            ================================================== */}

            <div className="summary-stats">
              {/* ACTIVITIES */}

              <div>
                <Activity size={18} />

                <span>Activities</span>

                <strong>{activities.length}</strong>
              </div>

              {/* PROJECTS */}

              <div>
                <Folder size={18} />

                <span>Projects</span>

                <strong>
                  {Array.isArray(summary?.projects)
                    ? summary.projects.length
                    : 0}
                </strong>
              </div>

              {/* TECHNOLOGIES */}

              <div>
                <Code2 size={18} />

                <span>Technologies</span>

                <strong>
                  {Array.isArray(summary?.technologies)
                    ? summary.technologies.length
                    : 0}
                </strong>
              </div>

              {/* GITHUB EVENTS */}

              <div>
                <GitBranch size={18} />

                <span>GitHub Events</span>

                <strong>{githubActivity?.count ?? 0}</strong>
              </div>
            </div>

            {/* ==================================================
                CREATE POST
            ================================================== */}

            <button
              className="create-post-button"
              onClick={createPost}
              disabled={postLoading}
            >
              <Sparkles size={18} />

              <span>
                {postLoading ? "Creating post..." : "Turn this into a post"}
              </span>

              <ArrowRight size={20} />
            </button>

            {/* GENERATED POST */}

            {generatedPost && (
              <div className="generated-post">
                <p>{generatedPost}</p>
              </div>
            )}
          </section>

          {/* ==================================================
              TODAY'S ACTIVITY
          ================================================== */}

          <section className="card activity-card">
            <h2>Today's Activity</h2>

            {/* ACTIVITIES */}

            <div className="activity-row">
              <div className="activity-icon">
                <Activity size={18} />
              </div>

              <span>Activities</span>

              <strong>{activities.length}</strong>
            </div>

            {/* PROJECTS */}

            <div className="activity-row">
              <div className="activity-icon">
                <Folder size={18} />
              </div>

              <span>Projects</span>

              <strong>
                {Array.isArray(summary?.projects) ? summary.projects.length : 0}
              </strong>
            </div>

            {/* TECHNOLOGIES */}

            <div className="activity-row">
              <div className="activity-icon">
                <Code2 size={18} />
              </div>

              <span>Technologies</span>

              <strong>
                {Array.isArray(summary?.technologies)
                  ? summary.technologies.length
                  : 0}
              </strong>
            </div>

            {/* GITHUB EVENTS */}

            <div className="activity-row">
              <div className="activity-icon">
                <GitBranch size={18} />
              </div>

              <span>GitHub Events</span>

              <strong>{githubActivity?.count ?? 0}</strong>
            </div>
          </section>

          {/* ==================================================
              PROJECTS
          ================================================== */}

          <section className="card">
            <div className="card-heading">
              <h2>Projects</h2>
            </div>

            <div className="tag-list">
              {Array.isArray(summary?.projects) &&
                summary.projects.map((project, index) => (
                  <div className="data-item" key={index}>
                    {typeof project === "string" ? project : project.name}
                  </div>
                ))}
            </div>
          </section>

          {/* ==================================================
              TECHNOLOGIES
          ================================================== */}

          <section className="card">
            <div className="card-heading">
              <h2>Technologies</h2>
            </div>

            <div className="tag-list">
              {Array.isArray(summary?.technologies) &&
                summary.technologies.map((technology, index) => (
                  <div className="technology-item" key={index}>
                    <span>
                      {typeof technology === "string"
                        ? technology
                        : technology.name}
                    </span>
                  </div>
                ))}
            </div>
          </section>

          {/* ==================================================
              ACCOMPLISHMENTS
          ================================================== */}

          <section className="card full-card">
            <h2>Accomplishments</h2>

            {Array.isArray(summary?.accomplishments) &&
              summary.accomplishments.map((item, index) => (
                <div className="list-item" key={index}>
                  • {typeof item === "string" ? item : item.description}
                </div>
              ))}
          </section>

          {/* ==================================================
              PROBLEMS SOLVED
          ================================================== */}

          <section className="card full-card">
            <h2>Problems Solved</h2>

            {Array.isArray(summary?.problems_solved) &&
              summary.problems_solved.map((item, index) => (
                <div className="list-item" key={index}>
                  • {typeof item === "string" ? item : item.description}
                </div>
              ))}
          </section>
        </main>
      )}
    </div>
  );
};

export default Dashboard;
