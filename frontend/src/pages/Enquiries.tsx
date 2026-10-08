import { useEffect, useState } from "react";
import { apiRequest } from "../services/api";

type Enquiry = {
  id: string;
  student_name: string;
  student_email: string;
  student_phone: string;
  nationality: string;
  course: string;
  intake: string;
  status: string;
  assigned_counsellor: string | null;
  notes: Note[];
  status_history: StatusHistory[];
  created_at: string;
  updated_at: string;
};

type Note = {
  author_id: string;
  content: string;
  created_at: string;
};

type StatusHistory = {
  status: string;
  changed_by: string;
  changed_at: string;
};

type Pagination = {
  page: number;
  limit: number;
  total: number;
  pages: number;
};

const STATUSES = [
  "new",
  "contacted",
  "documents pending",
  "applied",
  "visa in process",
  "closed",
];

function Enquiries() {
  const [enquiries, setEnquiries] = useState<Enquiry[]>([]);
  const [pagination, setPagination] = useState<Pagination>({
    page: 1,
    limit: 10,
    total: 0,
    pages: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedEnquiry, setSelectedEnquiry] =
    useState<Enquiry | null>(null);

  const [showCreateForm, setShowCreateForm] = useState(false);

  const [studentName, setStudentName] = useState("");
  const [studentEmail, setStudentEmail] = useState("");
  const [studentPhone, setStudentPhone] = useState("");
  const [nationality, setNationality] = useState("");
  const [course, setCourse] = useState("");
  const [intake, setIntake] = useState("");
  const [assignedCounsellor, setAssignedCounsellor] = useState("");

  const [newNote, setNewNote] = useState("");

  const [actionLoading, setActionLoading] = useState(false);

  const loadEnquiries = async (page = pagination.page) => {
    setLoading(true);
    setError("");

    try {
      const data = await apiRequest(
        `/enquiries?page=${page}&limit=10`
      );

      setEnquiries(data.items);
      setPagination({
        page: data.page,
        limit: data.limit,
        total: data.total,
        pages: data.pages,
      });
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load enquiries");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEnquiries(1);
  }, []);

  const resetCreateForm = () => {
    setStudentName("");
    setStudentEmail("");
    setStudentPhone("");
    setNationality("");
    setCourse("");
    setIntake("");
    setAssignedCounsellor("");
  };

  const createEnquiry = async (
    event: React.FormEvent
  ) => {
    event.preventDefault();

    setActionLoading(true);
    setError("");

    try {
      await apiRequest("/enquiries", {
        method: "POST",
        body: JSON.stringify({
          student_name: studentName,
          student_email: studentEmail,
          student_phone: studentPhone,
          nationality,
          course,
          intake,
          assigned_counsellor:
            assignedCounsellor || null,
        }),
      });

      resetCreateForm();
      setShowCreateForm(false);

      await loadEnquiries(1);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to create enquiry");
      }
    } finally {
      setActionLoading(false);
    }
  };

  const updateEnquiry = async (
    field: "status" | "assigned_counsellor",
    value: string
  ) => {
    if (!selectedEnquiry) {
      return;
    }

    setActionLoading(true);
    setError("");

    try {
      await apiRequest(
        `/enquiries/${selectedEnquiry.id}`,
        {
          method: "PATCH",
          body: JSON.stringify({
            [field]: value || null,
          }),
        }
      );

      const data = await apiRequest(
        `/enquiries/${selectedEnquiry.id}`
      );

      setSelectedEnquiry(data);

      await loadEnquiries(pagination.page);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to update enquiry");
      }
    } finally {
      setActionLoading(false);
    }
  };

  const addNote = async () => {
    if (!selectedEnquiry || !newNote.trim()) {
      return;
    }

    setActionLoading(true);
    setError("");

    try {
      await apiRequest(
        `/enquiries/${selectedEnquiry.id}/notes`,
        {
          method: "POST",
          body: JSON.stringify({
            content: newNote.trim(),
          }),
        }
      );

      const data = await apiRequest(
        `/enquiries/${selectedEnquiry.id}`
      );

      setSelectedEnquiry(data);
      setNewNote("");

      await loadEnquiries(pagination.page);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to add note");
      }
    } finally {
      setActionLoading(false);
    }
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString();
  };

  const formatDateTime = (date: string) => {
    return new Date(date).toLocaleString();
  };

  return (
    <section className="enquiries-page">
      <div className="enquiries-header">
        <div>
          <h2>Student Enquiries</h2>
          <p>
            Manage and track student counselling enquiries.
          </p>
        </div>

        <div className="enquiries-actions">
          <button
            className="refresh-button"
            onClick={() => loadEnquiries(pagination.page)}
          >
            🔄 Refresh
          </button>

          <button
            className="create-button"
            onClick={() => setShowCreateForm(true)}
          >
            + New Enquiry
          </button>
        </div>
      </div>

      {error && (
        <div className="enquiries-error">
          {error}
        </div>
      )}

      {showCreateForm && (
        <div className="enquiry-form-card">
          <div className="form-card-header">
            <div>
              <h3>Create New Enquiry</h3>
              <p>Enter the student's enquiry details.</p>
            </div>

            <button
              className="close-button"
              onClick={() => {
                setShowCreateForm(false);
                resetCreateForm();
              }}
            >
              ✕
            </button>
          </div>

          <form
            className="enquiry-form"
            onSubmit={createEnquiry}
          >
            <div className="form-grid">
              <div className="form-group">
                <label>Student Name</label>

                <input
                  type="text"
                  value={studentName}
                  onChange={(event) =>
                    setStudentName(event.target.value)
                  }
                  placeholder="Enter student name"
                  required
                />
              </div>

              <div className="form-group">
                <label>Email</label>

                <input
                  type="email"
                  value={studentEmail}
                  onChange={(event) =>
                    setStudentEmail(event.target.value)
                  }
                  placeholder="student@example.com"
                  required
                />
              </div>

              <div className="form-group">
                <label>Phone</label>

                <input
                  type="text"
                  value={studentPhone}
                  onChange={(event) =>
                    setStudentPhone(event.target.value)
                  }
                  placeholder="+92..."
                  required
                />
              </div>

              <div className="form-group">
                <label>Nationality</label>

                <input
                  type="text"
                  value={nationality}
                  onChange={(event) =>
                    setNationality(event.target.value)
                  }
                  placeholder="Nationality"
                  required
                />
              </div>

              <div className="form-group">
                <label>Course</label>

                <input
                  type="text"
                  value={course}
                  onChange={(event) =>
                    setCourse(event.target.value)
                  }
                  placeholder="e.g. BS Computer Science"
                  required
                />
              </div>

              <div className="form-group">
                <label>Intake</label>

                <input
                  type="text"
                  value={intake}
                  onChange={(event) =>
                    setIntake(event.target.value)
                  }
                  placeholder="e.g. Fall 2027"
                  required
                />
              </div>

              <div className="form-group">
                <label>Assigned Counsellor</label>

                <input
                  type="text"
                  value={assignedCounsellor}
                  onChange={(event) =>
                    setAssignedCounsellor(event.target.value)
                  }
                  placeholder="Counsellor ID (optional)"
                />
              </div>
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="cancel-button"
                onClick={() => {
                  setShowCreateForm(false);
                  resetCreateForm();
                }}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="create-button"
                disabled={actionLoading}
              >
                {actionLoading
                  ? "Creating..."
                  : "Create Enquiry"}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="enquiries-card">
        {loading ? (
          <div className="enquiries-loading">
            Loading enquiries...
          </div>
        ) : enquiries.length === 0 ? (
          <div className="enquiries-empty">
            No enquiries found.
          </div>
        ) : (
          <>
            <div className="table-wrapper">
              <table className="enquiries-table">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Course</th>
                    <th>Intake</th>
                    <th>Status</th>
                    <th>Counsellor</th>
                    <th>Created</th>
                    <th></th>
                  </tr>
                </thead>

                <tbody>
                  {enquiries.map((enquiry) => (
                    <tr key={enquiry.id}>
                      <td>
                        <div className="student-cell">
                          <strong>
                            {enquiry.student_name}
                          </strong>

                          <span>
                            {enquiry.student_email}
                          </span>
                        </div>
                      </td>

                      <td>{enquiry.course}</td>

                      <td>{enquiry.intake}</td>

                      <td>
                        <span
                          className={`status-badge status-${enquiry.status
                            .replaceAll(" ", "-")
                            .toLowerCase()}`}
                        >
                          {enquiry.status}
                        </span>
                      </td>

                      <td>
                        {enquiry.assigned_counsellor ||
                          "Unassigned"}
                      </td>

                      <td>
                        {formatDate(enquiry.created_at)}
                      </td>

                      <td>
                        <button
                          className="view-button"
                          onClick={() =>
                            setSelectedEnquiry(enquiry)
                          }
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pagination">
              <button
                disabled={pagination.page <= 1}
                onClick={() =>
                  loadEnquiries(pagination.page - 1)
                }
              >
                ← Previous
              </button>

              <span>
                Page {pagination.page} of{" "}
                {pagination.pages || 1}
              </span>

              <button
                disabled={
                  pagination.page >= pagination.pages
                }
                onClick={() =>
                  loadEnquiries(pagination.page + 1)
                }
              >
                Next →
              </button>
            </div>
          </>
        )}
      </div>

      {selectedEnquiry && (
        <div
          className="modal-overlay"
          onClick={() => setSelectedEnquiry(null)}
        >
          <div
            className="enquiry-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <h2>
                  {selectedEnquiry.student_name}
                </h2>

                <p>
                  {selectedEnquiry.student_email}
                </p>
              </div>

              <button
                className="close-button"
                onClick={() =>
                  setSelectedEnquiry(null)
                }
              >
                ✕
              </button>
            </div>

            <div className="detail-grid">
              <div>
                <span>Phone</span>
                <strong>
                  {selectedEnquiry.student_phone}
                </strong>
              </div>

              <div>
                <span>Nationality</span>
                <strong>
                  {selectedEnquiry.nationality}
                </strong>
              </div>

              <div>
                <span>Course</span>
                <strong>
                  {selectedEnquiry.course}
                </strong>
              </div>

              <div>
                <span>Intake</span>
                <strong>
                  {selectedEnquiry.intake}
                </strong>
              </div>

              <div>
                <span>Created</span>
                <strong>
                  {formatDateTime(
                    selectedEnquiry.created_at
                  )}
                </strong>
              </div>

              <div>
                <span>Updated</span>
                <strong>
                  {formatDateTime(
                    selectedEnquiry.updated_at
                  )}
                </strong>
              </div>
            </div>

            <div className="detail-section">
              <h3>Manage Enquiry</h3>

              <div className="management-grid">
                <div className="form-group">
                  <label>Status</label>

                  <select
                    value={selectedEnquiry.status}
                    disabled={actionLoading}
                    onChange={(event) =>
                      updateEnquiry(
                        "status",
                        event.target.value
                      )
                    }
                  >
                    {STATUSES.map((status) => (
                      <option
                        value={status}
                        key={status}
                      >
                        {status}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Assigned Counsellor</label>

                  <input
                    type="text"
                    value={
                      selectedEnquiry.assigned_counsellor ||
                      ""
                    }
                    disabled={actionLoading}
                    placeholder="Counsellor ID"
                    onChange={(event) =>
                      setSelectedEnquiry({
                        ...selectedEnquiry,
                        assigned_counsellor:
                          event.target.value,
                      })
                    }
                    onBlur={() =>
                      updateEnquiry(
                        "assigned_counsellor",
                        selectedEnquiry.assigned_counsellor ||
                          ""
                      )
                    }
                  />
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>Add Note</h3>

              <div className="note-form">
                <textarea
                  value={newNote}
                  onChange={(event) =>
                    setNewNote(event.target.value)
                  }
                  placeholder="Write a note about this student..."
                  rows={3}
                />

                <button
                  className="create-button"
                  disabled={
                    actionLoading || !newNote.trim()
                  }
                  onClick={addNote}
                >
                  Add Note
                </button>
              </div>
            </div>

            <div className="detail-section">
              <h3>Notes History</h3>

              {selectedEnquiry.notes.length === 0 ? (
                <p className="empty-text">
                  No notes added yet.
                </p>
              ) : (
                <div className="history-list">
                  {selectedEnquiry.notes
                    .slice()
                    .reverse()
                    .map((note, index) => (
                      <div
                        className="history-item"
                        key={index}
                      >
                        <div>
                          <strong>
                            Counsellor
                          </strong>

                          <span>
                            {formatDateTime(
                              note.created_at
                            )}
                          </span>
                        </div>

                        <p>{note.content}</p>
                      </div>
                    ))}
                </div>
              )}
            </div>

            <div className="detail-section">
              <h3>Status History</h3>

              <div className="history-list">
                {selectedEnquiry.status_history
                  .slice()
                  .reverse()
                  .map((history, index) => (
                    <div
                      className="history-item"
                      key={index}
                    >
                      <div>
                        <strong>
                          {history.status}
                        </strong>

                        <span>
                          {formatDateTime(
                            history.changed_at
                          )}
                        </span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default Enquiries;