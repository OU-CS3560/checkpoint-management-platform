import { useState, useEffect } from "react";

import { Form as RouterForm, useSubmit, useActionData } from "react-router-dom";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";

export default function ClassroomBasicInfoPanel({ classroom }) {
  const submit = useSubmit();
  const [mode, setMode] = useState("view");
  const [name, setName] = useState(classroom.name);
  const [beginDate, setBeginDate] = useState(classroom.begin_date);
  const [endDate, setEndDate] = useState(classroom.end_date);
  const [githubClassroomLink, setGithubClassroomLink] = useState(
    classroom.github_classroom_link || ""
  );

  // Use the action data from the route.
  const actionResult = useActionData();

  // Check actionResult variable when it is changing.
  // Set mode to view if the API call was a success.
  useEffect(() => {
    // When not submitted, it will be undefined.
    // When submitted with out errors, it will be null
    // When submitted with errors, the keys count will not be zero.
    if (actionResult !== null && actionResult !== undefined) {
      const { status, data } = actionResult;
      if (status === "success") {
        setMode("view");
      } else if (status === "error") {
      }
    }
  }, [actionResult]);

  // Unpack the errors from the API's result.
  let errors = {};
  if (actionResult !== null && actionResult !== undefined) {
    const { status, data } = actionResult;
    if (status === "error") {
      errors = data;
    }
  }

  if (mode === "view") {
    return (
      <>
        <Row>
          <Col>
            <h1>{classroom.name}</h1>
            <p>
              Begin: {new Date(classroom.begin_date).toDateString()} End:{" "}
              {new Date(classroom.end_date).toDateString()}
            </p>
            {classroom.github_classroom_link ? (
              <a
                href={classroom.github_classroom_link}
                target="_blank"
                rel="noreferrer"
              >
                GitHub Classroom
              </a>
            ) : (
              <></>
            )}
          </Col>
        </Row>
        <Row className="mb-3">
          <Col xs={3}>
            <Button variant="outline-primary" onClick={() => setMode("edit")}>
              Edit
            </Button>
            <Button
              variant="outline-primary"
              onClick={() =>
                submit(null, {
                  method: "delete",
                })
              }
            >
              Delete
            </Button>
          </Col>
        </Row>
      </>
    );
  } else if (mode === "edit") {
    return (
      <>
        <Row>
          <Col>
            <Form as={RouterForm} method="patch" id="update-classroom-form">
              <Row className="mb-3">
                <Form.Group as={Col} className="mb-3" controlId="name">
                  <Form.Label>Name</Form.Label>
                  <Form.Control
                    name="name"
                    type="text"
                    value={name}
                    onChange={(e) => {
                      setName(e.target.value);
                    }}
                    isInvalid={!!errors.name}
                  />
                  <Form.Control.Feedback type="invalid">
                    {errors.name}
                  </Form.Control.Feedback>
                </Form.Group>
              </Row>
              <Row className="mb-3">
                <Form.Group as={Col} className="mb-3" controlId="begin-date">
                  <Form.Label>Begin Date</Form.Label>
                  <Form.Control
                    name="begin_date"
                    type="date"
                    value={beginDate}
                    onChange={(e) => {
                      setBeginDate(e.target.value);
                    }}
                    isInvalid={!!errors.begin_date}
                  />
                  <Form.Control.Feedback type="invalid">
                    {errors.begin_date}
                  </Form.Control.Feedback>
                </Form.Group>
                <Form.Group as={Col} className="mb-3" controlId="end-date">
                  <Form.Label>End Date</Form.Label>
                  <Form.Control
                    name="end_date"
                    type="date"
                    value={endDate}
                    onChange={(e) => {
                      setEndDate(e.target.value);
                    }}
                    isInvalid={!!errors.end_date}
                  />
                  <Form.Control.Feedback type="invalid">
                    {errors.end_date}
                  </Form.Control.Feedback>
                </Form.Group>
              </Row>
              <Row className="mb-3">
                <Form.Group
                  as={Col}
                  className="mb-3"
                  controlId="github-classroom-link"
                >
                  <Form.Label>GitHub Classroom</Form.Label>
                  <Form.Control
                    name="github_classroom_link"
                    type="text"
                    value={githubClassroomLink}
                    onChange={(e) => {
                      setGithubClassroomLink(e.target.value);
                    }}
                    isInvalid={!!errors.github_classroom_link}
                  />
                  <Form.Control.Feedback type="invalid">
                    {errors.github_classroom_link}
                  </Form.Control.Feedback>
                </Form.Group>
              </Row>
              <Row>
                <Col xs={3}>
                  <Button
                    variant="outline-primary"
                    onClick={(e) => {
                      submit(e.currentTarget);
                    }}
                    type="submit"
                  >
                    Save
                  </Button>
                  <Button
                    variant="outline-primary"
                    onClick={() => setMode("view")}
                  >
                    Cancel
                  </Button>
                </Col>
              </Row>
            </Form>
          </Col>
        </Row>
      </>
    );
  }
}
