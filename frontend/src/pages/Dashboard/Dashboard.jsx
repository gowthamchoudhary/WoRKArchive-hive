import { useEffect, useState } from "react";
import {
  getGithubMe,
  getGithubActivity,
  getGithubActivities,
  getWorkSummary,
} from "../../api/github";
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

import "./Dashboard.css";

const Dashboard = () => {
  const [postTime, setPostTime] = useState("");
  const [github, setGithub] = useState(null);
  const [githubActivity, setGithubActivity] = useState(null);
  const [activities, setActivities] = useState([]);
  const [summary, setSummary] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadDashboard() {
    if (!postTime) {
      setError("Please select your post time.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const [
        githubData,
        githubActivityData,
        activitiesData,
        summaryData,
      ] = await Promise.all([
        getGithubMe(),
        getGithubActivity(postTime),
        getGithubActivities(postTime),
        getWorkSummary(postTime),
      ]);

      setGithub(githubData);
      setGithubActivity(githubActivityData);
      setActivities(activitiesData);
      setSummary(summaryData.llm_summary);
    } catch (error) {
      console.error("Dashboard error:", error);

      if (error.response) {
        setError(
          error.response.data?.detail ||
            "Could not load dashboard"
        );
      } else {
        setError("Could not connect to the server");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="dashboard">

      {/* NAVBAR */}

      <header className="dashboard-nav">

        <div className="brand">
          <div className="brand-icon">✦</div>
          <span>LOGS</span>
        </div>

        <nav>
          <button className="nav-active">
            Overview
          </button>

          <button>
            Create
          </button>

          <button>
            History
          </button>
        </nav>

        <div className="nav-right">

          <Bell size={20} strokeWidth={1.8} />

          <Settings size={20} strokeWidth={1.8} />

          {github && (
            <div className="profile">

              {github.avatar_url ? (
                <img
                  src={github.avatar_url}
                  alt=""
                />
              ) : (
                <div className="profile-letter">
                  {github.username?.[0]?.toUpperCase()}
                </div>
              )}

              <span>{github.username}</span>

              <ChevronDown size={16} />
            </div>
          )}

        </div>

      </header>


      {/* TIME SELECTOR */}

      <div className="dashboard-controls">

        <label>
          Post time
        </label>

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


      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}


      {/* DASHBOARD CONTENT */}

      {!summary && !loading ? (
        <div className="empty-dashboard">
          <h2>Ready when you are.</h2>
          <p>
            Choose your post time to load your work summary.
          </p>
        </div>
      ) : (

        <main className="dashboard-grid">

          {/* MAIN SUMMARY CARD */}

          <section className="summary-card">

            <div className="summary-header">

              <div>
                <p className="eyebrow">
                  TODAY
                </p>

                <h1>
                  Your work, remembered.
                </h1>

                <p className="subtitle">
                  LOGS analyzed your activity and generated
                  this summary.
                </p>
              </div>

              <div className="date-pill">
                <CalendarDays size={17} />

                <span>
                  Today
                </span>
              </div>

            </div>


            {/* AI SUMMARY */}

            {summary?.summary && (
              <div className="ai-summary">
                {summary.summary}
              </div>
            )}


            {/* STATS */}

            <div className="summary-stats">

              <div>
                <Activity size={18} />

                <span>
                  Activities
                </span>

                <strong>
                  {activities.length}
                </strong>
              </div>


              <div>
                <Folder size={18} />

                <span>
                  Projects
                </span>

                <strong>
                  {Array.isArray(summary?.projects)
                    ? summary.projects.length
                    : 0}
                </strong>
              </div>


              <div>
                <Code2 size={18} />

                <span>
                  Technologies
                </span>

                <strong>
                  {Array.isArray(summary?.technologies)
                    ? summary.technologies.length
                    : 0}
                </strong>
              </div>


              <div>
                <GitBranch size={18} />

                <span>
                  GitHub Events
                </span>

                <strong>
                  {githubActivity?.count ?? 0}
                </strong>
              </div>

            </div>


            <button className="create-post-button">

              <Sparkles size={18} />

              <span>
                Turn this into a post
              </span>

              <ArrowRight size={20} />

            </button>

          </section>


          {/* TODAY'S ACTIVITY */}

          <section className="card activity-card">

            <h2>
              Today's Activity
            </h2>

            <div className="activity-row">

              <div className="activity-icon">
                <Activity size={18} />
              </div>

              <span>
                Activities
              </span>

              <strong>
                {activities.length}
              </strong>

            </div>


            <div className="activity-row">

              <div className="activity-icon">
                <Folder size={18} />
              </div>

              <span>
                Projects
              </span>

              <strong>
                {Array.isArray(summary?.projects)
                  ? summary.projects.length
                  : 0}
              </strong>

            </div>


            <div className="activity-row">

              <div className="activity-icon">
                <Code2 size={18} />
              </div>

              <span>
                Technologies
              </span>

              <strong>
                {Array.isArray(summary?.technologies)
                  ? summary.technologies.length
                  : 0}
              </strong>

            </div>


            <div className="activity-row">

              <div className="activity-icon">
                <GitBranch size={18} />
              </div>

              <span>
                GitHub Events
              </span>

              <strong>
                {githubActivity?.count ?? 0}
              </strong>

            </div>

          </section>


          {/* PROJECTS */}

          <section className="card">

            <div className="card-heading">

              <h2>
                Projects
              </h2>

            </div>

            <div className="tag-list">

              {Array.isArray(summary?.projects) &&
                summary.projects.map((project, index) => (

                  <div
                    className="data-item"
                    key={index}
                  >
                    {typeof project === "string"
                      ? project
                      : project.name}
                  </div>

                ))}

            </div>

          </section>


          {/* TECHNOLOGIES */}

          <section className="card">

            <div className="card-heading">

              <h2>
                Technologies
              </h2>

            </div>

            <div className="tag-list">

              {Array.isArray(summary?.technologies) &&
                summary.technologies.map((technology, index) => (

                  <div
                    className="technology-item"
                    key={index}
                  >
                    <span>
                      {typeof technology === "string"
                        ? technology
                        : technology.name}
                    </span>
                  </div>

                ))}

            </div>

          </section>


          {/* ACCOMPLISHMENTS */}

          <section className="card full-card">

            <h2>
              Accomplishments
            </h2>

            {Array.isArray(summary?.accomplishments) &&
              summary.accomplishments.map(
                (item, index) => (

                  <div
                    className="list-item"
                    key={index}
                  >
                    •{" "}
                    {typeof item === "string"
                      ? item
                      : item.description}
                  </div>

                )
              )}

          </section>


          {/* PROBLEMS SOLVED */}

          <section className="card full-card">

            <h2>
              Problems Solved
            </h2>

            {Array.isArray(summary?.problems_solved) &&
              summary.problems_solved.map(
                (item, index) => (

                  <div
                    className="list-item"
                    key={index}
                  >
                    •{" "}
                    {typeof item === "string"
                      ? item
                      : item.description}
                  </div>

                )
              )}

          </section>

        </main>

      )}

    </div>
  );
};

export default Dashboard;