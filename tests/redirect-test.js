
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
};

const BASE_URL = 'http://localhost:8000';
const SHORT_CODE = 'PHPs8s';

export default function () {
  const response = http.get(
    `${BASE_URL}/${SHORT_CODE}`,
    { redirects: 0 }
  );

  check(response, {
    'redirect returns HTTP 307': (r) => r.status === 307,
    'redirect has a Location header': (r) =>
      Boolean(r.headers.Location),
  });
}
