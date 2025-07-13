export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  full_name: string;
}

export interface UserCreate {
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user'
}

export interface TokenData {
  user_id?: string;
  email?: string;
  role?: UserRole;
  exp?: number;
  iat?: number;
}
