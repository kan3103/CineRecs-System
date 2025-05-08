import routes from './routes/index';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Fragment } from 'react';
import ProtectedRoute from './pages/ProtectRoute';

function App() {
  return (
      <BrowserRouter>
          <Routes>
              {routes.map((route, index) => {
                  const Page = route.component;
                  console.log('route layout', route.layout);
                  let Layout;
                  Layout = Fragment;
                  // if (route.layout) {
                  //     api = DefaultLayout;
                  // } else if (route.layoutStaff) {
                  //     api = LayoutStaff;
                  // } else {
                  //
                  // }
                  const allowedRoles = route.allowedRoles || [];

                  const element = (
                      <Layout>
                          <Page />
                      </Layout>
                  );

                  return route.protected ? (
                      <Route
                          key={index}
                          path={route.path}
                          element={
                              <ProtectedRoute allowedRoles={allowedRoles}>
                                  {element}
                              </ProtectedRoute>
                          }
                      />
                  ) : (
                      <Route key={index} path={route.path} element={element} />
                  );
              })}
          </Routes>
      </BrowserRouter>
  );
}

export default App;