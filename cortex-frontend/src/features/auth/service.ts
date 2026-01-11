import { http } from '../../lib/http';
import type { User, UserUpdateProfile } from '../../types';

export const getCurrentUser = async (): Promise<User> => {
  const response = await http.get<User>('/users/me');
  return response.data;
};

export const updateProfile = async (data: UserUpdateProfile): Promise<User> => {
  const response = await http.put<User>('/users/me', data);
  return response.data;
};
