// The standalone page: mount the essay, and report height when framed.
import "./abm.css";
import resultsUrl from "./results.json?url";
import { mount } from "./app.js";
import { reportHeight } from "../../shared/embed.js";

mount(document.getElementById("sama-abm"), { results: resultsUrl })
  .then(reportHeight)
  .catch((e) => console.error(e));
