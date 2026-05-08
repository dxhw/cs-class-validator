import React, { useState, useEffect } from "react";

// --- Interfaces ---
interface ValidateRequest {
  year: number;
  degree_type: string;
  degree: string;
  requirement_version: string;
  courses: string[];
  capstone_incomplete: boolean;
  old_constraints: Record<string, boolean>;
  new_constraints: Record<string, boolean>;
  max_unknowns: number;
}

interface PathwayDetails {
  Core: string;
  Additional: string;
  Intermediates: string[];
}

interface ValidationResultDetails {
  valid: boolean;
  unknowns: number;
  results_dict?:
    | Record<string, string[] | Record<string, PathwayDetails>>
    | Record<string, string>;
}

interface ValidateResponse {
  success: boolean;
  degree_type: string;
  degree: string;
  requirement_version: string;
  old_result?: ValidationResultDetails;
  new_result?: ValidationResultDetails;
  error?: string;
}

const API_BASE = "http://127.0.0.1:8000"; // Leave blank if serving via FastAPI, or use "http://localhost:8000" if running a separate dev server

export default function App() {
  // --- Form State ---
  const [courseInput, setCourseInput] = useState<string>("");
  const [courses, setCourses] = useState<string[]>([]);
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [degree, setDegree] = useState<string>("CS");
  const [degreeType, setDegreeType] = useState<string>("AB");
  const [reqVersion, setReqVersion] = useState<string>("New");
  const [capstoneIncomplete, setCapstoneIncomplete] = useState<boolean>(false);
  const [maxUnknowns, setMaxUnknowns] = useState<number>(20);
  const [showConstraints, setShowConstraints] = useState<boolean>(false);
  const [oldConstraints, setOldConstraints] = useState<Record<string, boolean>>(
    {},
  );
  const [newConstraints, setNewConstraints] = useState<Record<string, boolean>>(
    {},
  );

  // --- UI/Result State ---
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<ValidateResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>("");

  // Static options based on your server.py
  const degrees = ["CS", "CompBio", "CS+ECON", "MATH+CS", "APMA+CS"];
  const degreeTypes = ["AB", "SCB"];
  const availableVersions =
    degree === "CS" ? ["Old", "New", "Either"] : ["New"];

  // Fetch default constraints when degree or version changes
  useEffect(() => {
    const fetchConstraints = async () => {
      try {
        if (reqVersion === "Either") {
          const res = await fetch(`${API_BASE}/constraints/${degree}`);
          if (!res.ok) throw new Error("Constraints not available.");
          const data = await res.json();

          setOldConstraints(data.Old || {});
          setNewConstraints(data.New || {});
        } else {
          const res = await fetch(
            `${API_BASE}/constraints/${degree}/${reqVersion}`,
          );
          if (!res.ok) throw new Error("Constraints not available.");
          const data = await res.json();

          if (reqVersion === "Old") {
            setOldConstraints(data);
            setNewConstraints({});
          } else {
            setNewConstraints(data);
            setOldConstraints({});
          }
        }
      } catch (err: any) {
        setOldConstraints({});
        setNewConstraints({});
        console.error(err);
      }
    };
    fetchConstraints();
  }, [degree, reqVersion]);

  // Auto-switch to "New" if a non-CS degree is selected
  useEffect(() => {
    if (degree !== "CS" && reqVersion !== "New") {
      setReqVersion("New");
    }
  }, [degree, reqVersion]);

  // --- Handlers ---
  // Handlers for toggling specific constraints
  const handleOldConstraintToggle = (key: string) => {
    setOldConstraints((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleNewConstraintToggle = (key: string) => {
    setNewConstraints((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleAddCourse = (e: React.FormEvent) => {
    e.preventDefault();

    const newCourses = courseInput
      .split(/[;,\n]+/)
      .map((course) => {
        // 1. Trim whitespace and capitalize
        let cleaned = course.trim().replaceAll("\"", "").toUpperCase();

        // 2. Use Regex to capture 3-4 letters, ignore existing spaces, and capture the numbers/letters that follow
        // ^([A-Z]{3,4}) : Captures exactly 3 or 4 uppercase letters at the start
        // \s* : Consumes any spaces the user might have already typed
        // (\d.*)$       : Captures the first digit and everything after it until the end
        const match = cleaned.match(/^([A-Z]{3,4})\s*(\d.*)$/);

        if (match) {
          // 3. Reconstruct the string with exactly one space
          return `${match[1]} ${match[2]}`;
        }

        // If it doesn't match the pattern (e.g. they typed nonsense), just return what they typed
        return cleaned;
      })
      .filter((course) => course.length > 0);

    if (newCourses.length > 0) {
      setCourses([...courses, ...newCourses]);
    }

    setCourseInput("");
  };

  const handleRemoveCourse = (indexToRemove: number) => {
    setCourses(courses.filter((_, index) => index !== indexToRemove));
  };

  const handleClearCourses = () => {
    if (window.confirm("Are you sure you want to clear all courses?")) {
      setCourses([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    setResponse(null);

    const payload: ValidateRequest = {
      year,
      degree_type: degreeType,
      degree,
      requirement_version: reqVersion,
      courses,
      capstone_incomplete: capstoneIncomplete,
      old_constraints: oldConstraints,
      new_constraints: newConstraints,
      max_unknowns: maxUnknowns,
    };

    try {
      const res = await fetch(`${API_BASE}/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to validate degree plan");
      }
      setResponse(data);
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  /// --- Helpers ---
  const getUnknownsText = () => {
    if (!response?.success) return null;

    const oldValid = response.old_result?.valid;
    const newValid = response.new_result?.valid;

    // Safely grab the integer, default to 0 if undefined
    const oldCount = response.old_result?.unknowns ?? 0;
    const newCount = response.new_result?.unknowns ?? 0;

    if (oldValid && newValid) {
      if (oldCount === newCount) return `(Requires ${oldCount} unknowns)`;
      return `(Requires ${oldCount} unknowns for Old, ${newCount} unknowns for New)`;
    } else if (oldValid) {
      return `(Requires ${oldCount} unknowns)`;
    } else if (newValid) {
      return `(Requires ${newCount} unknowns)`;
    }

    return null;
  };

  /// --- Render Helpers ---
  const renderResultDetails = (
    title: string,
    result?: ValidationResultDetails,
  ) => {
    if (!result) return null;
    return (
      <div
        style={{
          marginTop: "1rem",
          padding: "1rem",
          border: "1px solid #ccc",
          borderRadius: "8px",
        }}
      >
        <h3>{title}</h3>
        <p>
          <strong>Status:</strong> {result.valid ? "✅ Valid" : "❌ Invalid"}
        </p>

        {result.results_dict && Object.keys(result.results_dict).length > 0 && (
          <div>
            <h4>Requirement Breakdown:</h4>
            <ul style={{ lineHeight: "1.6" }}>
              {Object.entries(result.results_dict).map(([reqName, reqData]) => {
                // 1. Handle the nested "pathways" dictionary
                if (
                  reqName === "pathways" &&
                  typeof reqData === "object" &&
                  !Array.isArray(reqData)
                ) {
                  const pathwaysData = reqData as Record<
                    string,
                    PathwayDetails
                  >;
                  const pathwayNames = Object.keys(pathwaysData);

                  return (
                    <li key={reqName} style={{ marginTop: "0.5rem" }}>
                      <strong>pathways:</strong>
                      {pathwayNames.length === 0 ? (
                        <em> None mapped</em>
                      ) : (
                        <ul
                          style={{
                            marginTop: "0.25rem",
                            listStyleType: "square",
                          }}
                        >
                          {Object.entries(pathwaysData).map(
                            ([pName, pDetails]) => (
                              <li
                                key={pName}
                                style={{ marginBottom: "0.5rem" }}
                              >
                                <strong>{pName} Pathway</strong>
                                <ul
                                  style={{
                                    listStyleType: "circle",
                                    marginLeft: "1rem",
                                  }}
                                >
                                  <li>
                                    <strong>Core:</strong> {pDetails.Core}
                                  </li>
                                  <li>
                                    <strong>Additional:</strong>{" "}
                                    {pDetails.Additional}
                                  </li>
                                  <li>
                                    <strong>Intermediates:</strong>{" "}
                                    {pDetails.Intermediates.length > 0 ? (
                                      pDetails.Intermediates.join(", ")
                                    ) : (
                                      <em>None</em>
                                    )}
                                  </li>
                                </ul>
                              </li>
                            ),
                          )}
                        </ul>
                      )}
                    </li>
                  );
                }

                // 2. Handle the nested "foundations" dictionary
                if (
                  reqName === "foundations" &&
                  typeof reqData === "object" &&
                  !Array.isArray(reqData)
                ) {
                  const foundationsData = reqData as Record<string, string>;
                  const foundationCategories = Object.keys(foundationsData);

                  return (
                    <li key={reqName} style={{ marginTop: "0.5rem" }}>
                      <strong>foundations:</strong>
                      {foundationCategories.length === 0 ? (
                        <em> None mapped</em>
                      ) : (
                        <ul
                          style={{
                            marginTop: "0.25rem",
                            listStyleType: "square",
                          }}
                        >
                          {Object.entries(foundationsData).map(
                            ([category, course]) => (
                              <li key={category}>
                                <strong>{category}:</strong> {course}
                              </li>
                            ),
                          )}
                        </ul>
                      )}
                    </li>
                  );
                }

                // 3. Handle standard lists (Intro, Math, Humanities, etc.)
                if (Array.isArray(reqData)) {
                  return (
                    <li key={reqName}>
                      <strong>{reqName}:</strong>{" "}
                      {reqData.length > 0 ? (
                        reqData.join(", ")
                      ) : (
                        <em>None mapped</em>
                      )}
                    </li>
                  );
                }

                return null;
              })}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div
      style={{
        maxWidth: "800px",
        margin: "0 auto",
        fontFamily: "sans-serif",
        padding: "2rem",
      }}
    >
      <h1>Brown CS Concentration Validator</h1>

      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}
      >
        {/* Model Parameters */}
        <section
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "1rem",
          }}
        >
          <label>
            Graduation Year:
            <input
              type="number"
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              style={{ display: "block", width: "100%" }}
            />
          </label>
          <label>
            Degree:
            <select
              value={degree}
              onChange={(e) => setDegree(e.target.value)}
              style={{ display: "block", width: "100%" }}
            >
              {degrees.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </label>
          <label>
            Degree Type:
            <select
              value={degreeType}
              onChange={(e) => setDegreeType(e.target.value)}
              style={{ display: "block", width: "100%" }}
            >
              {degreeTypes.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
          <label>
            Requirement Version:
            <select
              value={reqVersion}
              onChange={(e) => setReqVersion(e.target.value)}
              style={{ display: "block", width: "100%" }}
            >
              {/* Change versions.map to availableVersions.map */}
              {availableVersions.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </label>
          <label>
            Max Unknowns Allowed:
            <input
              type="number"
              min="0"
              max="40"
              value={maxUnknowns}
              onChange={(e) => setMaxUnknowns(Number(e.target.value))}
              style={{ display: "block", width: "100%" }}
            />
          </label>
          <label style={{ gridColumn: "span 2" }}>
            <input
              type="checkbox"
              checked={capstoneIncomplete}
              onChange={(e) => setCapstoneIncomplete(e.target.checked)}
            />
            Capstone Incomplete
          </label>
        </section>

        {/* Constraints Selection (Collapsible) */}
        <section
          style={{
            border: "1px solid #ddd",
            borderRadius: "8px",
            overflow: "hidden",
          }}
        >
          {/* Toggle Button */}
          <button
            type="button"
            onClick={() => setShowConstraints(!showConstraints)}
            style={{
              width: "100%",
              padding: "1rem",
              background: "var(--surface-bg)",
              border: "none",
              borderBottom: showConstraints ? "1px solid #ddd" : "none",
              textAlign: "left",
              fontSize: "1.1rem",
              fontWeight: "bold",
              cursor: "pointer",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            Customize Requirements
            <span>{showConstraints ? "▲" : "▼"}</span>
          </button>

          {/* Collapsible Content */}
          {showConstraints && (
            <div
              style={{
                width: "100%",
                padding: "1rem",
                background: "var(--surface-bg)",
                color: "var(--text-color)", // Added this to ensure arrow is visible
                border: "none",
                borderBottom: showConstraints
                  ? "1px solid var(--border-color)"
                  : "none",
                display: "flex",
                gap: "1rem",
                flexWrap: "wrap",
              }}
            >
              {/* Show Old Constraints if "Old" or "Either" is selected */}
              {(reqVersion === "Old" || reqVersion === "Either") &&
                Object.keys(oldConstraints).length > 0 && (
                  <div style={{ flex: 1, minWidth: "300px" }}>
                    <h3 style={{ marginTop: 0 }}>
                      Old Requirements Constraints
                    </h3>
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "0.5rem",
                      }}
                    >
                      {Object.entries(oldConstraints).map(([key, isActive]) => (
                        <label
                          key={key}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "0.5rem",
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={isActive}
                            onChange={() => handleOldConstraintToggle(key)}
                          />
                          {key}
                        </label>
                      ))}
                    </div>
                  </div>
                )}

              {/* Show New Constraints if "New" or "Either" is selected */}
              {(reqVersion === "New" || reqVersion === "Either") &&
                Object.keys(newConstraints).length > 0 && (
                  <div style={{ flex: 1, minWidth: "300px" }}>
                    <h3 style={{ marginTop: 0 }}>
                      New Requirements Constraints
                    </h3>
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "0.5rem",
                      }}
                    >
                      {Object.entries(newConstraints).map(([key, isActive]) => (
                        <label
                          key={key}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "0.5rem",
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={isActive}
                            onChange={() => handleNewConstraintToggle(key)}
                          />
                          {key}
                        </label>
                      ))}
                    </div>
                  </div>
                )}
            </div>
          )}
        </section>

        {/* Course Entry */}
        <section>
          <h3>Courses</h3>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "0.5rem",
              marginBottom: "1rem",
            }}
          >
            <textarea
              placeholder="e.g. CSCI 0150, CSCI 0200; MATH 0540 &#10;MATH 0100... (separate with commas, semicolons, or line breaks)"
              value={courseInput}
              onChange={(e) => setCourseInput(e.target.value)}
              onKeyDown={(e) => {
                // Pressing Enter WITHOUT holding Shift will submit the courses
                // Holding Shift + Enter will just add a new line in the box
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleAddCourse(e as any);
                }
              }}
              style={{
                width: "100%",
                minHeight: "100px", // Makes the box physically larger
                padding: "0.75rem",
                fontSize: "1.1rem", // Larger text
                fontFamily: "inherit",
                borderRadius: "4px",
                border: "1px solid #ccc",
                resize: "vertical", // Lets the user drag to make it even taller
              }}
            />
            {/* Action Buttons */}
            <div
              style={{ display: "flex", gap: "1rem", alignSelf: "flex-start" }}
            >
              <button
                type="button"
                onClick={handleAddCourse}
                style={{
                  padding: "0.75rem 1.5rem",
                  fontSize: "1rem",
                  cursor: "pointer",
                  borderRadius: "4px",
                  border: "1px solid #ccc",
                }}
              >
                Add Course(s)
              </button>

              {courses.length > 0 && (
                <button
                  type="button"
                  onClick={handleClearCourses}
                  style={{
                    padding: "0.75rem 1.5rem",
                    fontSize: "1rem",
                    cursor: "pointer",
                    backgroundColor: "#f8d7da",
                    color: "#721c24",
                    border: "1px solid #f5c6cb",
                    borderRadius: "4px",
                  }}
                >
                  Clear All Courses
                </button>
              )}
            </div>
          </div>

          <ul
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "0.5rem",
              listStyle: "none",
              padding: 0,
            }}
          >
            {/* Grab the index from the map function */}
            {courses.map((course, index) => (
              // Use a combination of course and index for a truly unique key
              <li
                key={`${course}-${index}`}
                style={{
                  background: "var(--surface-bg)",
                  padding: "0.25rem 0.5rem",
                  borderRadius: "4px",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                }}
              >
                {course}
                {/* Pass the index to the remove function */}
                <button
                  type="button"
                  onClick={() => handleRemoveCourse(index)}
                  style={{
                    background: "transparent",
                    border: "none",
                    cursor: "pointer",
                    color: "red",
                  }}
                >
                  &times;
                </button>
              </li>
            ))}
          </ul>
        </section>
        {/* Policy Warning for Old CS Requirements > 2027 */}
        {degree === "CS" &&
          year > 2027 &&
          (reqVersion === "Old" || reqVersion === "Either") && (
            <div
              style={{
                backgroundColor: "#f8d7da",
                color: "#721c24",
                padding: "1rem",
                borderRadius: "4px",
                border: "1px solid #f5c6cb",
                marginTop: "1rem",
              }}
            >
              <strong>🚫 Policy Notice:</strong> Students graduating after 2027
              are not eligible to use the Old CS requirements.{" "}
              {reqVersion === "Either"
                ? "The old requirements validation will automatically fail."
                : "Please switch to the New requirements."}
            </div>
          )}
        {/* Slow Model Warning */}
        {(reqVersion === "Old" || reqVersion === "Either") &&
          degree === "CS" &&
          degreeType === "SCB" &&
          maxUnknowns > 10 && (
            <div
              style={{
                backgroundColor: "#fff3cd",
                color: "#856404",
                padding: "1rem",
                borderRadius: "4px",
                border: "1px solid #ffeeba",
                marginTop: "1rem",
              }}
            >
              <strong>⚠️ Performance Warning:</strong> Validating the Old CS SCB
              requirements with a high number of unknowns ({maxUnknowns}) can
              take a significant amount of time to compute. Please be patient
              after clicking validate.
            </div>
          )}
        {/* Model Validity Warning */}
        <div
          style={{
            backgroundColor: "#fff3cd",
            color: "#856404",
            padding: "1rem",
            borderRadius: "4px",
            border: "1px solid #ffeeba",
            marginTop: "1rem",
          }}
        >
          <strong>⚠️ Validity Warning:</strong> Please note that this is a
          student project, and our model's results has no say in actual
          concentration approval. If you are truly evaluating your ability to
          graduate, please speak with your concentration advisor.
        </div>
        {/* Model Failing Warning - Intro*/}
        {!courses.includes("CSCI 0200") && !courses.includes("CSCI 0190") && (
          <div
            style={{
              backgroundColor: "#f8d7da",
              color: "#721c24",
              padding: "1rem",
              borderRadius: "4px",
              border: "1px solid #f5c6cb",
              marginTop: "1rem",
            }}
          >
            <strong>🚫 Known Bug Warning:</strong> If you have not completed the
            CS intro sequence (you have taken neither CSCI 0190 nor CSCI 0200),
            our model will automatically fail due to a known bug. Please include
            one of these courses in your course plan.
          </div>
        )}

        <button
          type="submit"
          disabled={loading || courses.length === 0}
          style={{ padding: "0.75rem", fontSize: "1rem", cursor: "pointer" }}
        >
          {loading ? "Validating..." : "Validate Degree Plan"}
        </button>
      </form>

      {/* Results Section */}
      {errorMsg && (
        <div style={{ color: "red", marginTop: "1rem" }}>
          <strong>Error:</strong> {errorMsg}
        </div>
      )}

      {response && (
        <div
          style={{
            marginTop: "2rem",
            padding: "1rem",
            background: response.success ? "var(--success-bg-muted)" : "var(--error-bg-muted)",
          }}
        >
          {/* Results Section */}
          {errorMsg && (
            <div style={{ color: "red", marginTop: "1rem" }}>
              <strong>Error:</strong> {errorMsg}
            </div>
          )}

          {response && (
            <div
              style={{
                marginTop: "2rem",
                padding: "1rem",
                background: response.success ? "var(--success-bg)" : "var(--error-bg)",
                borderRadius: "8px",
              }}
            >
              {/* UPDATED HEADER */}
              <h2
                style={{
                  display: "flex",
                  alignItems: "center",
                  flexWrap: "wrap",
                  gap: "0.75rem",
                  marginTop: 0,
                }}
              >
                <span>
                  Overall Result:{" "}
                  {response.success ? "✅ SUCCESS" : "❌ FAILED"}
                </span>

                {/* Conditional Unknowns Text */}
                {response.success && (
                  <span
                    style={{
                      fontSize: "1.2rem",
                      fontWeight: "normal",
                      color: "var(--text-muted)",
                    }}
                  >
                    {getUnknownsText()}
                  </span>
                )}
              </h2>

              {renderResultDetails(
                "New Version Requirements",
                response.new_result,
              )}
              {renderResultDetails(
                "Old Version Requirements",
                response.old_result,
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
